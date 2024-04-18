import json
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import AppTokenIsCorrect
from ..models import IntegrationsData
from .serializers import CallDataInfoSerializer, IntegrationsDataSerializer, FormResponseSerializer
from ..service.bitrix_integration import (
    BitrixDealCreationFields,
    _BitrixDealCreationFields,
    create_bitrix_deal,
    _create_bitrix_deal,
    get_deal_info,
    move_deal_to_doubles_stage,
)
from ..service.exceptions import (
    ScenarioNotFoundError,
    UnsuccessfulLeadCreationError,
    CategoryNotFoundError,
    SkorozvonAPIError,
)
from ..service.google_sheet_integration import (
    send_to_google_sheet,
    is_unique_data,
)
from ..service.telegram_integration import send_message_to_tg

logger = logging.getLogger(__name__)


def flatten_data(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


class FormResponseAPI(CreateAPIView):
    serializer_class = FormResponseSerializer

    @staticmethod
    def get_str_form_response(form_response: list):
        return settings.FORM_SPLIT_QUESTION_SYMBOL.join([
            f"{question.get('question_name', '').replace(settings.FORM_SPLIT_ANSWER_SYMBOL, '')}"
            f"{settings.FORM_SPLIT_ANSWER_SYMBOL}"
            f"{question.get('answer_values', '')[0]}"
            for question in form_response
        ])

    def post(self, request, *args, **kwargs):
        logger.info(json.dumps(request.data))
        data = flatten_data(request.data)
        data["form_response"] = self.get_str_form_response(request.data.get("form_response", dict()).get("answers", ""))
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            lead_info = _BitrixDealCreationFields(
                title="Анкетный",
                call_id=serializer.data["call_id"],
                name=serializer.data["lead_name"],
                phone=serializer.data["lead_phones"],
                comment=serializer.data["lead_comment"],
                scenario_id=serializer.data["call_scenario_id"],
                form=serializer.data["form_response"],
                result_id=serializer.data["call_result_id"],
            )
            try:
                _create_bitrix_deal(lead_info)
            except (ScenarioNotFoundError, UnsuccessfulLeadCreationError, CategoryNotFoundError, SkorozvonAPIError):
                pass
            except Exception:
                pass
        return Response(status=status.HTTP_201_CREATED)


class PhoneCallInfoAPI(CreateAPIView):
    serializer_class = CallDataInfoSerializer

    def post(self, request, *args, **kwargs):
        logger.info(json.dumps(request.data))
        serializer = self.serializer_class(data=flatten_data(request.data))
        if serializer.is_valid():
            serializer.save()
            lead_info = BitrixDealCreationFields(
                title="Лид",
                call_id=serializer.data["call_id"],
                name=serializer.data["lead_name"],
                phone=serializer.data["lead_phones"],
                comment=serializer.data["lead_comment"],
                scenario_id=serializer.data["call_scenario_id"],
                result_name=serializer.data["call_result_result_name"],
            )
            try:
                create_bitrix_deal(lead_info)
            except (ScenarioNotFoundError, UnsuccessfulLeadCreationError, CategoryNotFoundError, SkorozvonAPIError):
                pass
            except Exception:
                pass
        return Response(status=status.HTTP_201_CREATED)


class DealCreationHandlerAPI(APIView):
    permission_classes = [AppTokenIsCorrect]

    def post(self, request):
        deal_id = request.data["data[FIELDS][ID]"]
        cached_deal_id = cache.get(deal_id)
        if cached_deal_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        cache.set(deal_id, True, timeout=30)
        data = get_deal_info(request.data["data[FIELDS][ID]"])
        integration_by_id = IntegrationsData.objects.filter(stage_id=data["stage_id"])
        if integration_by_id.exists():
            if integration_by_id.count() > 1:
                integration_data = None
                integrations_data = IntegrationsDataSerializer(
                    IntegrationsData.objects.filter(stage_id=data["stage_id"]),
                    many=True
                )
                for integration in integrations_data.data:
                    integration_data = dict(integration)
                    if (
                            "МСК" in integration_data["sheet_name"] and data["city"] == "Москва" or
                            "МСК" not in integration_data["sheet_name"] and data["city"] != "Москва"
                    ):
                        break
            else:
                integration_data = IntegrationsDataSerializer(
                    IntegrationsData.objects.get(stage_id=data["stage_id"])).data
            # Проверяем, не является ли сделка дублем по номеру
            if integration_data["previous_sheet_names"]:
                previous_sheet_names = str(integration_data["previous_sheet_names"]).split(", ")
            else:
                previous_sheet_names = []
            if is_unique_data(
                    data["phone"],
                    integration_data["google_spreadsheet_id"],
                    integration_data["sheet_name"],
                    previous_sheet_names,
            ):
                send_to_google_sheet(
                    data,
                    data["stage_id"],
                    integration_data["google_spreadsheet_id"],
                    integration_data["sheet_name"],
                )
                send_message_to_tg(data, integration_data["tg_bot_id"])
            else:
                move_deal_to_doubles_stage(deal_id, data["stage_id"])
        cache.delete(deal_id)
        return Response(status=status.HTTP_200_OK)


class TestAPI(APIView):
    def post(self, request):
        return Response(status=status.HTTP_200_OK)
