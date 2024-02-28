from dataclasses import dataclass
from functools import wraps
import requests
import time

from django.conf import settings

from .exceptions import (
    UnsuccessfulLeadCreationError,
    CategoryNotFoundError,
    ScenarioNotFoundError,
)
from ..models import FieldIds, IntegrationsData, ScenarioIds
from .skorozvon_integration import skorozvon_api
from .telegram_integration import send_message_to_dev_chat, send_message_to_dev
from .yandex_disk_integration import get_file_share_link


def convert_date_to_ru(date: str):
    return ".".join(date.split("T")[0].split("-")[::-1])


def unify_phone(phone: str):
    # Приводим номер к единому формату
    replace_symbols = "+-_() "
    for replace_symbol in replace_symbols:
        phone = phone.replace(replace_symbol, "")
    if phone:
        return f"7{phone[-10:]}"
    return phone


def get_id_for_doubles_stage(stage_id: str):
    if ":" in stage_id:
        funnel_id = stage_id.split(":")[0].strip("C")
    else:
        funnel_id = stage_id
    stages = requests.get(settings.BITRIX_GET_DEAL_CATEGORY_STAGES_LIST, params={"ID": funnel_id}).json()["result"]
    doubles_id = [stage["STATUS_ID"] for stage in stages if stage["NAME"] == "Дубли"]
    if doubles_id:
        return doubles_id[0]
    else:
        return -1


def move_deal_to_doubles_stage(deal_id: str, stage_id: str):
    doubles_id = get_id_for_doubles_stage(stage_id)
    if doubles_id == -1:
        return
    requests.get(
        settings.BITRIX_UPDATE_DEAL,
        params={"ID": deal_id, "FIELDS[STAGE_ID]": doubles_id}
    )


def get_field_value_by_id(field_name: str, field_id: str) -> str:
    if field_id == "":
        return ""
    try:
        field_pair = FieldIds.objects.get(bitrix_field_name=field_name, bitrix_field_id=field_id)
        field_object = FieldIds._meta.get_field("bitrix_field_value")
        field_value = getattr(field_pair, field_object.attname)
    except FieldIds.DoesNotExist:
        field_value = ""
    return field_value


def get_deal_info(deal_id):
    deal = requests.get(settings.BITRIX_GET_DEAL_BY_ID, params={"ID": deal_id}).json()["result"]
    response = {
        "stage_id": deal["STAGE_ID"],
        "lead_name": deal["UF_CRM_1664819061161"],
        "phone": unify_phone(deal["UF_CRM_1665719874029"]),
        "lead_type": get_field_value_by_id("Тип лида", deal["UF_CRM_1664819174514"]),
        "lead_qualification": get_field_value_by_id("Квалификация лида", deal["UF_CRM_1664819117290"]),
        "lead_comment": deal["UF_CRM_1664819040131"],
        "link_to_audio": deal["UF_CRM_1664819217017"],
        "date": convert_date_to_ru(deal["DATE_MODIFY"]),
        "city": get_field_value_by_id("Город", deal["UF_CRM_1687464323171"]),
        "country": get_field_value_by_id("Страна", deal["UF_CRM_1688409961271"]),
        "car_mark": deal["UF_CRM_1694678311862"],
        "car_model": deal["UF_CRM_1694678343732"],
    }
    return response


def time_limit_signalization(func):
    """
    Декоратор для проверки времени выполнения функции
    Если время выполнения превышает TIME_LIMIT_MINUTES,
    То соответствующеесообщение отправляется в чат разработки
    """
    time_limit_minutes = 10

    @wraps(func)
    def wrap(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()
        upload_time_minutes = int((end_time - start_time) // 60)
        if upload_time_minutes > time_limit_minutes:
            send_message_to_dev_chat(
                f"Загрузка аудиофайла по звонку {args[0]['call_id']} составила {upload_time_minutes}."
            )
        return result
    return wrap


@dataclass
class BitrixDealCreationFields:
    title: str
    call_id: str
    name: str
    phone: str
    comment: str
    scenario_id: int
    result_name: str


@dataclass
class _BitrixDealCreationFields:
    title: str
    call_id: str
    name: str
    phone: str
    comment: str
    scenario_id: int
    form: str
    result_id: str


@time_limit_signalization
def _create_bitrix_deal(lead_info: BitrixDealCreationFields):
    # if lead_info.result_name.lower() not in settings.BITRIX_SUCCESSFUL_RESULT_NAMES:
    #     raise UnsuccessfulLeadCreationError(f"Result name '{lead_info.result_name}' is not successful")
    category_id = get_category_id(lead_info.scenario_id)
    call_data = skorozvon_api.get_call_audio(lead_info.call_id)
    share_link = get_file_share_link(call_data, lead_info.call_id)
    data = {
        "fields": {
            "TITLE": lead_info.title,
            "UF_CRM_1664819061161": lead_info.name,
            "UF_CRM_1665719874029": lead_info.phone,
            "UF_CRM_1664819217017": share_link,
            # "UF_CRM_1664819040131": lead_info.comment,
            "UF_CRM_1664819040131": lead_info.form,
            # "CATEGORY_ID": category_id,
            "CATEGORY_ID": "94",
        }
    }
    return requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)


@time_limit_signalization
def create_bitrix_deal(lead_info: BitrixDealCreationFields):
    if lead_info.result_name.lower() not in settings.BITRIX_SUCCESSFUL_RESULT_NAMES:
        raise UnsuccessfulLeadCreationError(f"Result name '{lead_info.result_name}' is not successful")
    category_id = get_category_id(lead_info.scenario_id)
    call_data = skorozvon_api.get_call_audio(lead_info.call_id)
    share_link = get_file_share_link(call_data, lead_info.call_id)
    data = {
        "fields": {
            "TITLE": lead_info.title,
            "UF_CRM_1664819061161": lead_info.name,
            "UF_CRM_1665719874029": lead_info.phone,
            "UF_CRM_1664819217017": share_link,
            # "UF_CRM_1664819040131": lead_info.comment,
            "UF_CRM_1664819040131": category_id,
            # "CATEGORY_ID": category_id,
            "CATEGORY_ID": "94",
        }
    }
    return requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)


def get_category_id(scenario_id):
    try:
        scenario = ScenarioIds.objects.get(scenario_id=scenario_id)
        searching_field = ScenarioIds._meta.get_field("scenario_name")
        scenario_name = getattr(scenario, searching_field.attname)
    except ScenarioIds.DoesNotExist:
        raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
    try:
        integration = IntegrationsData.objects.get(skorozvon_scenario_name=scenario_name)
        searching_field = IntegrationsData._meta.get_field("stage_id")
        stage_id = getattr(integration, searching_field.attname)
    except IntegrationsData.DoesNotExist:
        raise CategoryNotFoundError(f"Not found category according to scenario '{scenario_name}'")
    return stage_id.split(":")[0].strip("C") if ":" in stage_id else stage_id
