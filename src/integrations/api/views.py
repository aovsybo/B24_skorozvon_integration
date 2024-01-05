import os
import time
from datetime import datetime

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from telebot.apihelper import ApiTelegramException

from .serializers import CallInfoSerializer
from integrations.service.yandex_disk_integration import (
    upload_to_disk,
    get_file_share_link
)
from integrations.service.skorozvon_integration import get_call, get_calls
from integrations.service.bitrix_integration import (
    create_bitrix_deal,
    get_deal_info,
    get_category_id
)
from integrations.service.google_sheet_integration import (
    send_to_google_sheet,
    get_funnel_table_links,
    is_unique_data,
    get_table_data,
    get_funnel_info_from_integration_table,
)
from integrations.service.telegram_integration import (
    send_message_to_dev,
    send_message_to_dev_chat,
    send_fields_message,
    send_message,
)


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
            send_message_to_dev(f"Загрузка аудиофайла по звонку {data['call_id']} составила {upload_time_minutes}.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
        data, stage_id = get_deal_info(request.data["data[FIELDS][ID]"])
        integrations_table = get_funnel_info_from_integration_table()
        # TODO: П11 айдишник
        # Проверяем, находится ли данная стадия воронке в списке
        if stage_id in integrations_table['ID Стадии'].unique():
            integration_data = get_funnel_table_links(stage_id, integrations_table, data["city"])
            if is_unique_data(data, stage_id, integration_data["table_link"], integration_data["sheet_name"]):
                send_to_google_sheet(data, stage_id, integration_data["table_link"], integration_data["sheet_name"])
                # TODO: Рассылать в нужные чаты
                # send_fields_message(data, integration_data["tg"])
                send_message_to_dev_chat(f"Нужный чат: {integration_data['tg']}")
                send_fields_message(data, settings.TG_DEV_CHAT)
        return Response(status=status.HTTP_200_OK)


class GetCalls(APIView):
    def get(self, request):
        data = {
            "lead_name": "Иван",
            "phone": "7999213414",
            "lead_type": "49",
            "lead_qualification": "121",
            "lead_comment": "текст комментария.",
            "link_to_audio": "ссылка",
            "date": "2024-01-05",
            "city": "",
            "country": "Таиланд",
            "car_mark": "",
            "car_model": "",
        }
        stage_id = "C17:EXECUTING"
        integrations_table = get_funnel_info_from_integration_table()
        integration_data = get_funnel_table_links(stage_id, integrations_table, data["city"])
        send_to_google_sheet(data, stage_id, integration_data["table_link"], integration_data["sheet_name"])
        return Response(data=data, status=status.HTTP_200_OK)
