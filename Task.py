from UTILS.settings import AIDEVS2_API_KEY
import requests
from dotenv import load_dotenv

load_dotenv()



class ApiHandler:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.api_key = api_key

    def _get_url(self, endpoint, token):
        if endpoint is not None and token is not None:
            return f"{self.base_url}/{endpoint}/{token}"
        return f"{self.base_url}"

    def _post_request(self, endpoint=None, token=None, json=None,  headers=None, **kwargs):

        url = self._get_url(endpoint, token)
        response = requests.post(url, json=json, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def _get_request(self, endpoint, token):
        url = self._get_url(endpoint, token)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def authenticate_task(self, task_name):
        payload = {"apikey": self.api_key}
        return self._post_request('token', task_name, payload)["token"]

    def get_task(self, token):
        return self._get_request('task', token)

    def send_task(self, token, question, headers=None):
        return self._post_request('task', token, question, headers)

    def send_answer(self, token, answer, headers=None):
        return self._post_request('answer', token, answer, headers)


class Task:
    def __init__(self, task_name, send_response=False):
        self.api = ApiHandler(AIDEVS2_API_KEY, "https://zadania.aidevs.pl")
        self.task_name = task_name
        self.send_response = send_response

        self.task_token = self.api.authenticate_task(self.task_name)
        self.content = self.api.get_task(self.task_token)

    def send_task(self, question, headers=None):
        self.content = self.api.send_task(self.task_token, question, headers)
        print(self.content)
        return self.content

    def send_answer(self, answer, headers=None):
        return self.api.send_answer(self.task_token, answer, headers)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if self.send_response:
            result = self.send_answer(answer=self.content)
            print(result)
