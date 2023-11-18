import ast
import logging
import os
import io
import sys

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain.schema.output_parser import StrOutputParser

from Task import Task

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_dataframe_info(df):
    """
    Returns information about the DataFrame including its name (if set),
    column names, data types, and a flag indicating whether there are missing values in the column.
    """
    # Check if the DataFrame has a 'name' attribute
    df_name = getattr(df, 'name', 'Unnamed DataFrame')

    return str(pd.DataFrame({
        'DataFrame Name': df_name,
        'Column Name': df.columns,
        'Data Type': df.dtypes,
    })) + str(f'df.head(2): {df.head(2)}')


def _sanitize_output(text: str):
    logging.info(f'{text}')
    if '```' in text.lower() or 'python' in text.lower() or ast.parse(text):
        cmd = "\n".join([
            " ".join([word for word in line.split() if word.lower() != 'python'])
            for line in text.split("```")[1].splitlines()
        ])
        logging.info(f'{cmd} eval')

        result = eval(cmd).values[0]
        result = int(result) if isinstance(result, (np.int64, np.int32)) else float(result) if isinstance(result, (
        np.float64, np.float32)) else result
        logging.info(f'code output: {result} (type: {type(result)}) ')
        return result
    logging.info(f'Answer bases on model\'s knowledge {text}')
    return text


try:

    TASK_NAME = 'knowledge'
    with Task(task_name=TASK_NAME) as task:
        logging.info(f"Token for {task.task_name}: {task.task_token}")
        logging.info(f"Question: {task.content['question']}")
        currency_df = pd.DataFrame(requests.get('http://api.nbp.pl/api/exchangerates/tables/A').json()[0]['rates'])
        currency_df.name = 'currency_df'

        population_df = pd.DataFrame(requests.get('https://restcountries.com/v3.1/all').json())[['name', 'population']]

        population_df['Common country name'] = population_df['name'].apply(lambda x: x['common'])
        population_df['Official country name'] = population_df['name'].apply(lambda x: x['official'])
        population_df.name = 'population_df'
        del population_df['name']

        chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(""""
                "I require your assistance to respond to queries using one of two methods:

1. Simple and direct answer based on your knowledge. For example:
   User: What is the capital of Poland?
   AI: Warsaw

2. If the query involves data analysis, write a Python script using the schemas and metadata provided below. 
Your code response should be enclosed within triple backticks. Use original variable names For example:
   User: What is the population of Germany?
   AI: ```
       # Python code using the dataframe schema
       df_name_from_schema[df_name_from_schema['Common country name'] == 'Germany']['population']
       ```

Please adhere to the following schemas for data-related questions:

{schema_a}

-------------------

{schema_b}

### Context ###
Today is November 13, 2023

### RULES ###
- Choose ONLY ONE method for each response: either a simple answer or a Python script.
- No additional information, even comments.
- Use names of variables provided You in the metadata.
- Do not include any text between the triple backticks other than the Python code."

        
        
        
        """

                                                          ),
                HumanMessagePromptTemplate.from_template("{question}"),
            ])

        model = ChatOpenAI()

        chain = chat_template | model | StrOutputParser() | _sanitize_output


        logging.info("Invoking")
        logging.info(f"User: {task.content['question']}")
        response = chain.invoke({'schema_a': get_dataframe_info(currency_df), "schema_b" : get_dataframe_info(population_df), "question":task.content['question']})

        logging.info(f"{response}")
        final_answer = task.api._post_request(endpoint='answer', token=task.task_token,
                                                  json={'answer': str(response)})

        logging.info(final_answer)


except KeyError as ke:
    logging.error(ke)
    quit(-1)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
    quit(-1)





















