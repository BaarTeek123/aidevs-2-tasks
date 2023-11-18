import ast
import logging
import os
from datetime import datetime, timedelta
from PIL import Image
import io
import cv2
import requests
from dotenv import load_dotenv
from openai import OpenAI
from Task import Task

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    TASK_NAME = 'gnome'

    with (Task(task_name=TASK_NAME) as task):
        logging.info(f"Token for {task.task_name}: {task.task_token}")
        response = requests.get(task.content['url'])
        if response.status_code != 200:
            logging.error("Failed to download the image")
            raise Exception
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))
        image.show()

        #

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text":"""Return in polish just a color of dwarf's hat that is on his head. 
                         ### RULES:
                         - detect if dwarf is on the picture and return in POLISH LANGUAGE color of his hat
                         - if you cannot detect a dwarf  return "ERROR" as answer. 
                         - it can be animated dwarf
                         - Be very precise and strict
                         ### Example: 
                         ->  you detected blue hat on dwarf's head -> Answer: 'Niebieski'                  
                        
                         """},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": task.content['url'],
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )


        logging.info(f"{response.choices[0]}")
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': response.choices[0].message.content})

        logging.info(final_answer)


except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)





















