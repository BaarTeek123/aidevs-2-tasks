import json
import logging
import os
import sqlite3
import uuid

import pandas as pd
import qdrant_client
import requests
from Levenshtein import distance as lev_distance
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant

from Task import Task

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def find_closest_names(df, sentence):
    words = [s for s in sentence.split() if s.istitle()]

    # Create digrams from the sentence
    digrams = zip(words, words[1:])

    closest_match = None
    min_distance = float('inf')

    # Precompute unique distances
    unique_names = set(df['imie'].unique().tolist() + df['nazwisko'].unique().tolist())
    name_distances = {name: {word: lev_distance(name, word) for word in set(words)} for name in unique_names}

    for first_name, last_name in digrams:
        # Use apply method for vectorized distance calculation
        distances = df.apply(lambda row: name_distances[row['imie']].get(first_name, float('inf')) +
                                         name_distances[row['nazwisko']].get(last_name, float('inf')), axis=1)

        min_row_distance = distances.min()
        if min_row_distance < min_distance:
            min_distance = min_row_distance
            closest_match = df.iloc[distances.idxmin()]

    return closest_match


try:

    TASK_NAME = 'people'
    with Task(task_name=TASK_NAME) as task:
        logging.info(f"Token for {task.task_name}: {task.task_token}")
        response = requests.get(task.content['data'].split()[-1], stream=True)
        metadatas = json.loads(response.content)
        df = pd.DataFrame(metadatas)
        df['unique_id'] = [str(uuid.uuid4())for _ in range(len(df))]


        connection = sqlite3.connect('C03L05.db')
        df.to_sql(name='C03L05', con=connection, index=False, if_exists='replace')
        query = "SELECT * FROM C03L05;"

        df = pd.read_sql_query(query, connection)

        question = task.content['question']
        logging.info(f"Question {task.content['question']}")
        names = find_closest_names(df, question)
        logging.info(f"Question related to: {names['imie']} {names['nazwisko']}")

        embeddings = OpenAIEmbeddings()


        col_dfs = pd.DataFrame({'unique_id':  str(uuid.uuid4()), "column_name": col} for col in df.columns)
        rows = [
            {
                "id": row.unique_id,
                "payload": {"unique_id": row.unique_id, "content": row.column_name},
                "vector": embeddings.embed_documents([row.column_name])[0],
            }
            for row in col_dfs.itertuples()
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
            os.getenv('QDRANT_COLLECTION_NAME'), query_vector=embeddings.embed_query(question), limit=3
        )



        column = [i.payload['content'] for i in search if i.payload['content'] not in ['imie', 'nazwisko']]

        logging.info(10*'-' + f'\n{column}\n' + 10*'-' )


        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': names[column[0]]})

        logging.info(final_answer)


except KeyError as ke:
    logging.error(ke)
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)
finally:

    connection.close()




















