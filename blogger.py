import logging
from Task import Task
import os

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv, find_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')



SYSTEM_TEMPLATE = """As a Famous author of a cookbooks who writes his own blog IN POLISH LANGUAGE and nothing more and truthfully says "don't know" when the CONTEXT is not enough to give an answer.
Write short blog post (IN POLISH LANGUAGE, 4-5 sentences) about the following topic: {topic}"""


OPENAI_MODEL ='gpt-3.5-turbo'
chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL, streaming=True)
memory = ConversationBufferWindowMemory(k=1)
chain = ConversationChain(llm=chat, memory=memory)

try:
    TASK_NAME = 'blogger'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")

        answers = [
                f"Rozdział {i+1}" + chain.invoke(SYSTEM_TEMPLATE.format(topic=topic))['response']
                for i, topic in enumerate(task.content['blog'])
            ]
        print(answers)
        result = task.send_answer(answer={'apikey': task.api.api_key, 'answer': answers})
        print(result)

except KeyError as ke:
        logging.error('Something went wrong. No token or task found.')
        quit(-1)

except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        quit(-1)

















