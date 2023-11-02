from Task import ApiHandler
from UTILS.settings import OPENAI_API_KEY
from Task import Task
import logging


def moderate_text(text):
    api = ApiHandler(OPENAI_API_KEY, "https://api.openai.com/v1/moderations")
    data = {"input": text}
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    return  api._post_request(data=data, headers=headers)

def is_flagged(text) -> bool:
    return moderate_text(text)["results"][0]["flagged"]

def get_reasons(text) -> list:
    return [k for k,v in moderate_text(text)["results"][0]["category"].items() if v ]

try:
    TASK_NAME = 'moderation'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")

        result = task.send_answer(answer={'apikey': task.api.api_key, 'answer': [is_flagged(sent) for sent in task.content['input']]})
        print(result)

except KeyError as ke:
        logging.error('Something went wrong. No token or task found.')
        quit(-1)

except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        quit(-1)

