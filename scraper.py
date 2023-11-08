import logging
from time import sleep

from dotenv import load_dotenv
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from Task import Task

import requests

load_dotenv()



try:
    TASK_NAME = 'scraper'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Question: {task.content['msg']}")
        print(task.content['input'])

        counter = 0
        response = None
        while response is None and counter < 200:
            response = requests.get(task.content['input'])
            if response.status_code != 200:
                print(response, counter)

                response = None
            counter += 1
            sleep(0.01*counter)
            if response is not None:
                response = response.content
            else:
                response = ''

        llm = ChatOpenAI(callbacks=[StreamingStdOutCallbackHandler()], streaming=True)

        SYSTEM_TEMPLATE = f"""Basing on provided text: {task.content['msg']} \n ### context ###\n""" + response + '\n###'

        HUMAN_TEMPLATE = f"""{task.content['question']}"""

        answer = llm([
            SystemMessage(content=SYSTEM_TEMPLATE ),
            HumanMessage(content=HUMAN_TEMPLATE)

        ])


        print(answer)



        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': answer.content})

        print(final_answer)


except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















