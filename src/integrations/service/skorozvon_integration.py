from datetime import timedelta, datetime

import requests

from django.conf import settings


class SkorozvonAPI:
    _token = None
    BASE_URL = "https://app.skorozvon.ru/api/v2/"

    def __init__(self):
        self._token = self.get_token()

    @staticmethod
    def get_token():
        url = "https://app.skorozvon.ru/oauth/token"
        data = {
            "grant_type": "password",
            "username": settings.SKOROZVON_LOGIN,
            "api_key": settings.SKOROZVON_API_KEY,
            "client_id": settings.SKOROZVON_APPLICATION_ID,
            "client_secret": settings.SKOROZVON_APPLICATION_KEY,
        }
        token = requests.post(url, data=data).json()
        return f"Bearer {token['access_token']}"

    def get_request(self, endpoint_url, params=None, has_content=False):
        headers = {
            "Authorization": self._token
        }
        response = requests.get(self.BASE_URL + endpoint_url, params=params, headers=headers)
        if has_content:
            return response.content
        return response.json()

    def get_call_info(self, call_id: int):
        return self.get_request(f"calls/{call_id}")

    def get_calls_list(self):
        params = {
            "page": 3,
            "length": 100,
            "sort_by_time": True,
            "start_time": datetime.timestamp(datetime.utcnow() - timedelta(days=1))
        }
        return self.get_request("calls", params)

    def get_call_audio(self, call_id: int):
        return self.get_request(f"calls/{call_id}", has_content=True)


skorozvon_api = SkorozvonAPI()
