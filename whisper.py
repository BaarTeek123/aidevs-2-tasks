import logging

from dotenv import load_dotenv
from Task import Task


import requests
import openai



load_dotenv()


try:
    TASK_NAME = 'whisper'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Question: {task.content['msg']}")
        ### download file
        response = requests.get(task.content['msg'].split()[-1], stream=True)


        if response.status_code == 200:
            file_name = f"files/{task.content['msg'].split('/')[-1]}"

            with open(file_name, 'wb') as f:

                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
            audio_file = open(file_name, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format="text")

            # transcript = openai.Audio.translate("whisper-1", audio_file)

            final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': transcript})

            print(final_answer)




except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















