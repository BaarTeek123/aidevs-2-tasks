import logging
from Task import Task


try:
    TASK_NAME = 'inprompt'

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

















