import logging
from time import sleep

from dotenv import load_dotenv

from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from Task import Task
import string
# import requests

load_dotenv()

compare_strings_ignore_punctuation = lambda s1, s2: ''.join(filter(lambda x: x not in string.punctuation, s1)) == ''.join(filter(lambda x: x not in string.punctuation, s2))


try:
    TASK_NAME = 'whoami'
    info = ''
    while True:
        task = Task(task_name=TASK_NAME)
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Hint: {task.content['hint']}")
        info += task.content['hint'] + '\n'



        llm = ChatOpenAI(streaming=True)

        SYSTEM_TEMPLATE = f"""Basing on provided text information, provide my first and last name *** IMPORTANT *** 
        
        RULES: 
        - If You do not know yet or You are not sure, say "I do not know." then I will give you more information.
        - If You know, say just my first and last name. No further comments.
        , e.g. \
        IF YOU ARE SURE that I am Santa Clause return "Santa Clause". """


        HUMAN_TEMPLATE = f"""{info}"""

        answer = llm([
            SystemMessage(content=SYSTEM_TEMPLATE ),
            HumanMessage(content=HUMAN_TEMPLATE)

        ])
        sleep(0.5)

        print(answer)
        if 'I do not know'.lower() not in answer.content.lower():
            break



    final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': answer.content})

    print(final_answer)


except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















