import ast
import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from Task import Task

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)


try:
    TASK_NAME = 'tools'

    with (Task(task_name=TASK_NAME) as task):
        logging.info(f"Token for {task.task_name}: {task.task_token}")
        logging.info(f"Question: {task.content['question']}")

        SYSTEM_TEMPLATE = f'''
        "Decide classify the question

        ### RULES### :
        - classify the question to one of the following categories: [ToDO | Calendar]
        - Do not answer the question
        - Calendar should always contain a date -> use YYYY-MM-DD format
        - Be concise and return JSON response only and nothing else.

        ### Context ###
        Today is {datetime.now().weekday()}: {datetime.now().strftime('%Y-%m-%d')}.

        ### Examples ###
        Przypomnij mi, ze mam kupic mleko 
        {{"tool": "ToDo", "desc": "Kup mleko"}}
        'Jutro mam wizytę u lekarza 
        {{"tool": "Calendar", "desc": "Wizyta u lekarza", "date": {(datetime.now()+timedelta(days = 730)).strftime("%Y-%m-%d")} }}')
'''
        llm = ChatOpenAI(callbacks=[StreamingStdOutCallbackHandler()], streaming=True)

        response = llm([
            SystemMessage(content=SYSTEM_TEMPLATE),
            HumanMessage(content=task.content['question'])])




        logging.info(f"{response}")
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': ast.literal_eval(response.content)})

        logging.info(final_answer)




except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)





















