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
from integrations.service.skorozvon_integration import (
    get_call,
    get_calls
)
from integrations.service.bitrix_integration import (
    create_bitrix_deal,
    get_deal_info,
    get_category_id,
    get_id_for_doubles_stage,
)
from integrations.service.google_sheet_integration import (
    send_to_google_sheet,
    get_funnel_table_links,
    is_unique_data,
    get_funnel_info_from_integration_table,
)
from integrations.service.telegram_integration import (
    send_message_to_dev,
    send_message_to_tg,
)


CURRENT_DEALS = []


class BaseView(APIView):
    def get(self, request):
        return Response(data={"message": "ok"}, status=status.HTTP_200_OK)


class PhoneCallInfoAPI(APIView):
    def post(self, request):
        # Берем необходимые данные из запроса
        data = {
            "organisation_name": request.data["lead"]["name"],
            "organisation_phone": request.data["call"]["phone"],
            "comment": request.data["lead"]["comment"],
            "call_id": request.data["call"]["id"],
            "scenario_id": str(request.data["call"]["scenario_id"]),
        }
        deal_name = f"{request.data['call_result']['result_name']} {request.data['call_result']['result_id']}"
        start_time = time.time()
        # Сохраняем в БД данные пришедшие с запросом
        serializer = CallInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Загружаем запись на яндекс.диск и получаем ссылку
        call_content = get_call(data["call_id"])
        date_string = datetime.now().strftime("%d%m%Y%H%M%S")
        file_name = f"call_audio_{data['call_id']}_{date_string}.mp3"
        with open(f"{settings.BASE_DIR}/{file_name}", "wb") as f:
            f.write(call_content)
        upload_to_disk(settings.BASE_DIR, file_name)
        os.remove(f"{settings.BASE_DIR}/{file_name}")
        yandex_disk_link = get_file_share_link(file_name)
        # Создаем сделку в битриксе
        category_name = "[П44] ТЕСТ ИНТЕГРАЦИЙ"
        category_id = get_category_id(category_name)
        create_bitrix_deal(
            deal_name,
            data["organisation_name"],
            {"VALUE": data["organisation_phone"], "VALUE_TYPE": "WORK"},
            data["comment"],
            yandex_disk_link,
            category_id,
        )
        # Проверяем что весь процесс занял менее 10 минут
        # TODO: сделать через декоратор
        upload_time_minutes = int((time.time() - start_time) // 60)
        time_limit_minutes = 10
        if upload_time_minutes > time_limit_minutes:
            send_message_to_dev(f"Загрузка аудиофайла по звонку {data['call_id']} составила {upload_time_minutes}.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
        # TODO: token update
        deal_id = request.data["data[FIELDS][ID]"]
        # Проверяем соответствие передаваемого ключа и ключа битрикса
        # А также проверяем, не идет ли уже работа по данной сделке, чтобы не отправлять два раза на случай дубля
        if request.data["auth[application_token]"] != settings.BITRIX_APP_TOKEN or deal_id in CURRENT_DEALS:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            CURRENT_DEALS.append(request.data["data[FIELDS][ID]"])
        data, stage_id = get_deal_info(request.data["data[FIELDS][ID]"])
        integrations_table = get_funnel_info_from_integration_table()
        # Проверяем, находится ли данная стадия воронке в списке
        if stage_id in integrations_table['ID Стадии'].unique():
            integration_data = get_funnel_table_links(stage_id, integrations_table, data["city"])
            # Проверяем, не является ли сделка дублем по номеру
            if is_unique_data(
                    data["phone"],
                    integration_data["table_link"],
                    integration_data["sheet_name"],
                    integration_data["previous_sheet_names"]
            ):
                send_to_google_sheet(
                    data,
                    stage_id,
                    integration_data["table_link"],
                    integration_data["sheet_name"],
                )
                send_message_to_tg(data, integration_data["tg"])
        CURRENT_DEALS.remove(deal_id)
        return Response(status=status.HTTP_200_OK)


class GetCalls(APIView):
    def get(self, request):
        data = dict()
        stage_id = "C94:EXECUTING"
        data[stage_id] = get_id_for_doubles_stage(stage_id)
        return Response(data=data, status=status.HTTP_200_OK)
