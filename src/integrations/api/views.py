import os
import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CallInfoSerializer
from integrations.service.yandex_disk_integration import (
    upload_to_disk,
    get_file_share_link
)
from integrations.service.skorozvon_integration import get_call
from integrations.service.bitrix_integration import create_bitrix_deal, get_deal_info
from integrations.service.google_sheet_integration import send_to_google_sheet
from integrations.service.telegram_integration import send_message, send_fields_message


class BaseView(APIView):
    def get(self, request):
        return Response(data={"message": "ok"}, status=status.HTTP_200_OK)


class PhoneCallInfoAPI(APIView):
    def post(self, request):
        data = {
            "organisation_name": request.data["lead"]["name"],
            "organisation_phone": request.data["call"]["phone"],
            "comment": request.data["lead"]["comment"],
            "call_id": request.data["call"]["id"],
        }
        deal_name = f"{request.data['call_result']['result_name']} {request.data['call_result']['result_id']}"
        start_time = time.time()
        serializer = CallInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        call_content = get_call(data["call_id"])
        file_name = f"call_audio_{data['call_id']}.mp3"
        with open(file_name, "wb") as f:
            f.write(call_content)
        upload_to_disk(file_name)
        os.remove(file_name)
        yandex_disk_link = get_file_share_link(file_name)
        create_bitrix_deal(
            deal_name,
            data["organisation_name"],
            {"VALUE": data["organisation_phone"], "VALUE_TYPE": "WORK"},
            data["comment"],
            yandex_disk_link,
        )
        upload_time_minutes = int((time.time() - start_time) // 60)
        time_limit_minutes = 10
        if upload_time_minutes > time_limit_minutes:
            send_message(f"Загрузка аудиофайла по звонку {data['call_id']} составила {upload_time_minutes}.")
        print('Elapsed time: ', )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
        data = get_deal_info(request.data["data[FIELDS][ID]"][0])
        send_to_google_sheet(data)
        send_fields_message(data)
        send_fields_message(request.data)
        return Response(status=status.HTTP_200_OK)
