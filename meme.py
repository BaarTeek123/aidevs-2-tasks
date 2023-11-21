import logging
import os
import requests

from dotenv import load_dotenv
import json
from Task import Task

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)


try:
    TASK_NAME = 'meme'

    with Task(task_name=TASK_NAME) as task:
        logging.info(f"Token for {task.task_name}: {task.task_token}")


        url = "https://get.renderform.io/api/v2/render"

        headers = {
            'X-API-KEY': os.getenv('REDNER_API'),
            'Content-Type': 'application/json'
        }

        data = {
            "template": "itchy-badgers-agree-wildly-1027",
            "data": {
                "description.color": "#FFFFFF",
                "description.text": task.content['text'],
                "image.src": task.content['image']
            }
        }

        response = requests.post(url, json=data, headers=headers)

        x = json.loads(response.content)['href']
        #

        logging.info(f"{json.loads(response.content)['href']}")
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': str(json.loads(response.content)['href'])})

        logging.info(final_answer)




except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)





















