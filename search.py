import os
import uuid

import sqlite3
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
import qdrant_client
from langchain.text_splitter import CharacterTextSplitter

from dotenv import load_dotenv
import sqlalchemy
import pandas as pd
import logging
import requests


from Task import Task
import json


load_dotenv()


def get_chunks(text: str):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)


try:

    TASK_NAME = 'search'
    DB = 'sqlite3'
    # DB = 'my-sql'
    engine = None
    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        response = requests.get(task.content['msg'].split()[-1], stream=True)
        metadatas = json.loads(response.content)
        df = pd.DataFrame(metadatas)
        df['unique_id'] = [str(uuid.uuid4())for _ in range(len(df))]

        if DB == 'my-sql':
            engine = sqlalchemy.create_engine(os.getenv('SQL_CONNECTION')+"/AIDEVS")
            connection = engine.connect()
            df.to_sql(name='C03L04', con=engine, index=False, if_exists='replace')

            df = pd.read_sql_table('C03L04', con=connection)
        else:
            connection = sqlite3.connect('C03L04.db')
            df.to_sql(name='C03L04', con=connection, index=False, if_exists='replace')
            query = "SELECT * FROM C03L04;"

            df = pd.read_sql_query(query, connection)


        embeddings = OpenAIEmbeddings()

        rows = [
            {
                "id": row.unique_id,
                "payload": {"unique_id": row.unique_id, "content": row.url},
                "vector": embeddings.embed_documents([row.info])[0],
            }
            for row in df[:300].itertuples()
        ]

        ids, vectors, payloads = map(list, zip(*((row["id"], row["vector"], row["payload"]) for row in rows)))


        client = qdrant_client.QdrantClient(url=os.getenv('QDRANT_HOST'), api_key=os.getenv('QDRANT_API_KEY'))

        vectors_config = qdrant_client.http.models.VectorParams(
            size=1536,
            distance=qdrant_client.http.models.Distance.COSINE
        )

        client.recreate_collection(
            collection_name=os.getenv('QDRANT_COLLECTION_NAME'),
            vectors_config=vectors_config
        )

        # create vector store
        embeddings = OpenAIEmbeddings()

        vec_store = Qdrant(client=client, collection_name=os.getenv('QDRANT_COLLECTION_NAME'),
                           embeddings=embeddings)

        client.upsert(
            os.getenv('QDRANT_COLLECTION_NAME'),
            points=qdrant_client.http.models.Batch(ids=ids, payloads=payloads, vectors=vectors),
        )


        search = client.search(
            os.getenv('QDRANT_COLLECTION_NAME'), query_vector=embeddings.embed_query(task.content['question']), limit=1
        )

        logging.info(10*'-' + f'\n{search}\n' + 10*'-')

        selected_url = df.loc[df['unique_id'] == search[0].payload['unique_id'], 'url']

        logging.info(selected_url)

        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': selected_url.iloc[0]})

        logging.info(final_answer)


except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)
finally:
    if engine is not None:
        engine.dispose()
    connection.close()




















