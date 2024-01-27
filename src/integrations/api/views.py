import os
import time
from datetime import datetime

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CallInfoSerializer
from ..service.skorozvon_integration import skorozvon_api
from ..service.bitrix_integration import (
    create_bitrix_deal,
    get_deal_info,
    get_category_id,
    move_deal_to_doubles_stage,
)
from ..service.google_sheet_integration import (
    send_to_google_sheet,
    get_funnel_table_links,
    is_unique_data,
    get_funnel_info_from_integration_table,
)
from ..service.telegram_integration import (
    send_message_to_dev,
    send_message_to_tg,
)


CURRENT_DEALS = []


class PhoneCallInfoAPI(CreateAPIView):
    serializer_class = CallInfoSerializer

    def post(self, request, *args, **kwargs):
        # TODO: Save all to DB
        # TODO: Filtering request by scenario and result id (Oleg)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(create_bitrix_deal(serializer.data))
        # start_time = time.time()
        # # Загружаем запись на яндекс.диск и получаем ссылку
        # call_content = skorozvon_api.get_call_audio(serializer.data["call_id"])
        # date_string = datetime.now().strftime("%d%m%Y%H%M%S")
        # file_name = f"call_audio_{serializer.data['call_id']}_{date_string}.mp3"
        # with open(f"{settings.BASE_DIR}/{file_name}", "wb") as f:
        #     f.write(call_content)
        # upload_to_disk(settings.BASE_DIR, file_name)
        # os.remove(f"{settings.BASE_DIR}/{file_name}")
        # yandex_disk_link = get_file_share_link(file_name)
        # # Создаем сделку в битриксе
        # category_name = "[П44] ТЕСТ ИНТЕГРАЦИЙ"
        # category_id = get_category_id(category_name)
        # create_bitrix_deal(
        #     "Лид",
        #     serializer.data["organisation_name"],
        #     {"VALUE": serializer.data["organisation_phone"], "VALUE_TYPE": "WORK"},
        #     serializer.data["comment"],
        #     yandex_disk_link,
        #     category_id,
        # )
        # # Проверяем что весь процесс занял менее 10 минут
        # # TODO: сделать через декоратор
        # upload_time_minutes = int((time.time() - start_time) // 60)
        # time_limit_minutes = 10
        # if upload_time_minutes > time_limit_minutes:
        #     send_message_to_dev(f"Загрузка аудиофайла по звонку {data['call_id']} составила {upload_time_minutes}.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    def post(self, request):
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
            else:
                move_deal_to_doubles_stage(deal_id, stage_id)
        CURRENT_DEALS.remove(deal_id)
        return Response(status=status.HTTP_200_OK)


class TestAPI(APIView):
    def get(self, request):
        data = dict()
        data["call"] = skorozvon_api.get_call_info(881485321)
        # data["calls"] = skorozvon_api.get_calls_list()
        return Response(data=data, status=status.HTTP_200_OK)
