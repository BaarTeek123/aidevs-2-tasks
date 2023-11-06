import logging

from dotenv import load_dotenv
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from Task import Task



load_dotenv()



try:
    TASK_NAME = 'rodo'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Question: {task.content['msg']}")

        llm = ChatOpenAI(callbacks=[StreamingStdOutCallbackHandler()], streaming=True)
        SYSTEM_TEMPLATE = f"""
        {task.content['msg']}'
        """

        HUMAN_TEMPLATE = """Using placeholders that will hide your personal data. For: \n- '%imie%' for each first name \n'%nazwisko%' for each last name
        \n- last name: %nazwisko%\n- '%miasto%' for each city\n- '%zawod%' for each occupation \n- Tell me who You are? What are You doing?"""
        answer = llm([
            SystemMessage(content=SYSTEM_TEMPLATE),
            HumanMessage(content=HUMAN_TEMPLATE)


        ])

        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': HUMAN_TEMPLATE})

        print(final_answer)


except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















