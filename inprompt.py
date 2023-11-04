import logging
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

from UTILS.settings import OPENAI_API_KEY
from Task import Task


OPENAI_MODEL = 'gpt-3.5-turbo'


SYSTEM_TEMPLATE = ("""As a good person, answer a simple question. "
                   
                   ### context ###
                   {context}""")
try:
    TASK_NAME = 'inprompt'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        info_table = [Document(page_content=sentence, metadata = {"person": sentence.split()[0]})
                       for sentence in task.content['input']]
        print(f"Question: {task.content['question']}")
        ### filter documents:
        docs = [doc.page_content for doc in info_table if doc.metadata['person'] in task.content['question']]

        ### define model
        OPENAI_MODEL = 'gpt-3.5-turbo'
        chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL, streaming=True)
        memory = ConversationBufferWindowMemory(k=5)
        chain = ConversationChain(llm=chat, memory=memory)
        response = chain.invoke(SYSTEM_TEMPLATE.format(context="\n".join(docs)) + f"Question: {task.content['question']}")['response'].strip()

        ### send the answer
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token, json={'answer': response})
        print(final_answer)

except KeyError as ke:
        logging.error('Something went wrong. No token or task found.')
        quit(-1)

except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        quit(-1)

















