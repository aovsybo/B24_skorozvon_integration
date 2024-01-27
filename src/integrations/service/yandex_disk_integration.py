from datetime import datetime
import os
import requests

from django.conf import settings

import yadisk


def get_file_share_link(data, call_id):
    # TODO: Create TEMP file
    file_name = create_file_name(call_id)
    with open(f"{settings.BASE_DIR}/{file_name}", "wb") as f:
        f.write(data)
    upload_file_to_disk(file_name)
    os.remove(f"{settings.BASE_DIR}/{file_name}")
    return create_file_share_link(file_name)


def create_file_name(call_id: int):
    current_time = datetime.now().strftime("%d%m%Y_%H%M%S")
    return f"{call_id}_{current_time}.mp3"


def upload_file_to_disk(filename: str):
    # TODO: switch from uploading from filesystem to uploading from bytes
    y = yadisk.YaDisk(token=settings.YANDEX_DISK_TOKEN)
    y.upload(f"{settings.BASE_DIR}/{filename}", filename)


def create_file_share_link(filename: str):
    headers = {
        'Authorization': f'OAuth {settings.YANDEX_DISK_TOKEN}'
    }
    share_url = f"https://cloud-api.yandex.net/v1/disk/resources?path={filename}"
    share_response = requests.get(share_url, headers=headers)
    if share_response.status_code == 200:
        return share_response.json()["file"]
    return "Не удалось получить ссылку"
