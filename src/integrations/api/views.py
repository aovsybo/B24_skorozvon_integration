import os
import time
from datetime import datetime

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CallInfoSerializer
from integrations.service.yandex_disk_integration import (
    upload_to_disk,
    get_file_share_link
)
from integrations.service.skorozvon_integration import get_call, get_calls
from integrations.service.bitrix_integration import (
    create_bitrix_deal,
    get_deal_info,
    get_category_id,
    get_funnel_names_ids
)
from integrations.service.google_sheet_integration import (
    send_to_google_sheet,
    get_table,
    get_funnel_names,
    is_unique_data
)
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
            "scenario_id": str(request.data["call"]["scenario_id"]),
        }
        deal_name = f"{request.data['call_result']['result_name']} {request.data['call_result']['result_id']}"
        start_time = time.time()
        serializer = CallInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        call_content = get_call(data["call_id"])
        date_string = datetime.now().strftime("%d%m%Y%H%M%S")
        file_name = f"call_audio_{data['call_id']}_{date_string}.mp3"
        with open(f"{settings.BASE_DIR}/{file_name}", "wb") as f:
            f.write(call_content)
        upload_to_disk(settings.BASE_DIR, file_name)
        os.remove(f"{settings.BASE_DIR}/{file_name}")
        yandex_disk_link = get_file_share_link(file_name)
        category_name = "[П44] ТЕСТ ИНТЕГРАЦИЙ" # Заменить
        category_id = get_category_id(category_name)
        create_bitrix_deal(
            deal_name,
            data["organisation_name"],
            {"VALUE": data["organisation_phone"], "VALUE_TYPE": "WORK"},
            data["comment"],
            yandex_disk_link,
            category_id,
        )
        upload_time_minutes = int((time.time() - start_time) // 60)
        time_limit_minutes = 10
        if upload_time_minutes > time_limit_minutes:
            send_message(
                f"Загрузка аудиофайла по звонку {data['call_id']} составила {upload_time_minutes}.",
                settings.TG_DEV_ACCOUNT
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
        funnel_names = get_funnel_names()
        funnel_names_ids = get_funnel_names_ids(funnel_names)
        data, category_id, stage_id = get_deal_info(request.data["data[FIELDS][ID]"])
        if category_id in funnel_names_ids and stage_id == "EXECUTING" and is_unique_data(data):
            send_message(is_unique_data, settings.TG_DEV_ACCOUNT)
            integration_data = get_table(funnel_names_ids[category_id])
            send_to_google_sheet(data, integration_data["sheets"])
            send_fields_message(data, integration_data["tg"])
        return Response(status=status.HTTP_200_OK)


class GetCalls(APIView):
    def get(self, request):
        calls = get_calls()
        return Response(data={"calls": calls}, status=status.HTTP_200_OK)
