import logging

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from Task import Task

load_dotenv()

MODEL = 'text-embedding-ada-002'

SYSTEM_TEMPLATE = ("""As a good person, answer a simple question. "

                   ### context ###
                   {context}""")
try:
    TASK_NAME = 'embedding'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Question: {task.content['msg']}")

        keyword = "Hawaiian pizza"
        embeddings = OpenAIEmbeddings()
        query = embeddings.embed_query(keyword)
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token, json={'answer': query})
        print(final_answer)







except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















