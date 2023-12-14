import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CallInfoSerializer
from src.integrations.service.yandex_disk_integration import (
    upload_to_disk,
    get_file_share_link
)
from src.integrations.service.skorozvon_integration import get_call
from src.integrations.service.bitrix_integration import create_bitrix_deal, get_deal_info
from src.integrations.service.google_sheet_integration import send_to_google_sheet
from src.integrations.service.telegram_integration import send_message

# TODO: Привести ответы к общему виду и обрабатывать ошибка
class PhoneCallInfoAPI(APIView):
    def post(self, request):
        data = {
            "organisation_name": request.data["lead"]["name"],
            "organisation_phone": request.data["call"]["phone"],
            "comment": request.data["lead"]["comment"],
        }
        deal_name = f"{request.data['call_result']['result_name']} {request.data['call_result']['result_id']}"
        call_id = request.data["call"]["id"]
        call_content = get_call(call_id)
        file_name = f"call_audio_{call_id}.mp3"
        with open(file_name, "wb") as f:
            f.write(call_content)
        upload_to_disk(file_name)
        os.remove(file_name)
        data["yandex_disk_link"] = get_file_share_link(file_name)
        print(data["yandex_disk_link"].split("]")[0].strip("["))
        serializer = CallInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        create_bitrix_deal(
            deal_name,
            data["organisation_name"],
            {"VALUE": data["organisation_phone"], "VALUE_TYPE": "WORK"},
            data["comment"],
            data["yandex_disk_link"]
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
        data = get_deal_info()
        send_to_google_sheet(data)
        send_message(data)
        return Response(status=status.HTTP_200_OK)
