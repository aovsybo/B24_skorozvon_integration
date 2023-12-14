import requests

import yadisk

from django.conf import settings


def upload_to_disk(filename: str):
    y = yadisk.YaDisk(token=settings.YANDEX_DISK_TOKEN)
    y.upload(filename, filename)


def get_file_share_link(filename: str):
    headers = {
        'Authorization': f'OAuth {settings.YANDEX_DISK_TOKEN}'
    }
    share_url = f"https://cloud-api.yandex.net/v1/disk/resources?path={filename}"
    share_response = requests.get(share_url, headers=headers)
    if share_response.status_code == 200:
        return share_response.json()["file"]
    return "Не удалось получить ссылку"
