import requests

from django.conf import settings


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


def get_call(call_id: int):
    token = get_token()
    headers = {
        "Authorization": token
    }
    url = f"https://app.skorozvon.ru/api/v2/calls/{call_id}.mp3"
    response = requests.get(url, headers=headers)
    return response.content
