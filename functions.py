import logging

from dotenv import load_dotenv
from Task import Task



load_dotenv()

addUser = {
    "name": "addUser",
    "description": "Add multiple tasks to Todoist",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "user name"
                },
            "surname": {
                "type": "string",
                "description": "user surname"
                },
            "year": {
                "type": "integer",
                "description": "year of birth"
                }
            }
        }
}


try:
    TASK_NAME = 'functions'

    with Task(task_name=TASK_NAME) as task:
        print(f"Token for {task.task_name}: {task.task_token}")
        print(f"Question: {task.content['msg']}")



        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': addUser})

        print(final_answer)




except KeyError as ke:
    logging.error('Something went wrong. No token or task found.')
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)

















