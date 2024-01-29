from datetime import datetime, timedelta
import requests
import tempfile

from django.conf import settings

import yadisk


def get_file_share_link(data, call_id):
    file_name = create_file_name(call_id)
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        share_link = upload_file_to_disk(tmp.name, file_name)
    return share_link


def create_file_name(call_id: int):
    current_time = (datetime.now() + timedelta(hours=3)).strftime("%d%m%Y_%H%M%S")
    return f"call_audio_{call_id}_{current_time}.mp3"


def upload_file_to_disk(tmp_file_name, yandex_filename: str):
    y = yadisk.YaDisk(token=settings.YANDEX_DISK_TOKEN)
    y.upload(tmp_file_name, yandex_filename)
    return y.get_download_link(yandex_filename)
