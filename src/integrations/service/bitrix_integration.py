from functools import wraps
import requests
import time

from django.conf import settings

from .db import (
    get_integrations_if_exist,
    get_category_id,
    get_form_field_id_by_form_field_name,
    get_bitrix_field_id,
)
from .exceptions import UnsuccessfulLeadCreationError
from .skorozvon_integration import skorozvon_api
from .telegram_integration import send_message_to_dev_chat, send_message_to_tg
from .validation import SkorozvonForm, SkorozvonCall, BitrixDeal
from .yandex_disk_integration import get_file_share_link
from ..service.google_sheet_integration import send_to_google_sheet, is_unique_data


def get_id_for_stage_by_name(stage_id: str, stage_names: list[str]) -> list:
    if ":" in stage_id:
        funnel_id = stage_id.split(":")[0].strip("C")
    else:
        funnel_id = stage_id
    stages = requests.get(settings.BITRIX_GET_DEAL_CATEGORY_STAGES_LIST, params={"ID": funnel_id}).json()["result"]
    stages_ids = [stage["STATUS_ID"] for stage in stages if stage["NAME"] in stage_names]
    return stages_ids if stages_ids else []


def get_id_for_doubles_stage(stage_id: str):
    stage_ids = get_id_for_stage_by_name(stage_id, ["Дубли"])
    if stage_ids:
        return stage_ids[0]
    return -1


def get_ids_for_invalid_stages(stage_id: str):
    stage_ids = get_id_for_stage_by_name(stage_id, ["Невостребованный лид", "Не прошёл KPI"])
    if stage_ids:
        return stage_id
    return -1


def move_deal_to_doubles_stage(deal_id: str, stage_id: str):
    doubles_id = get_id_for_doubles_stage(stage_id)
    if doubles_id == -1:
        return
    requests.get(
        settings.BITRIX_UPDATE_DEAL,
        params={"ID": deal_id, "FIELDS[STAGE_ID]": doubles_id}
    )


def get_deal_info(deal_id) -> BitrixDeal:
    response = requests.get(settings.BITRIX_GET_DEAL_BY_ID, params={"ID": deal_id}).content
    return BitrixDeal.model_validate_json(response)


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


@time_limit_signalization
def create_bitrix_deal_by_form(lead_info: SkorozvonForm):
    # if lead_info.result_name.lower() not in settings.BITRIX_SUCCESSFUL_RESULT_NAMES:
    #     raise UnsuccessfulLeadCreationError(f"Result name '{lead_info.result_name}' is not successful")
    category_id = get_category_id(lead_info.scenario_id)
    call_data = skorozvon_api.get_call_audio(lead_info.call_id)
    share_link = get_file_share_link(call_data, lead_info.call_id)
    data = {
        "TITLE": lead_info.title,
        "UF_CRM_1664819061161": lead_info.name,
        "UF_CRM_1665719874029": lead_info.phone,
        "UF_CRM_1664819217017": share_link,
        "UF_CRM_1664819040131": lead_info.scenario_id,
        "CATEGORY_ID": "94",
        # "CATEGORY_ID": category_id,
    }
    for qa in lead_info.form.split(settings.FORM_SPLIT_QUESTION_SYMBOL):
        question, answer = qa.split(settings.FORM_SPLIT_ANSWER_SYMBOL)
        form_field_id = get_form_field_id_by_form_field_name(question)
        if form_field_id:
            data[form_field_id] = get_bitrix_field_id(question, answer)

    return requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json={"fields": data})


@time_limit_signalization
def create_bitrix_deal_by_call(lead_info: SkorozvonCall):
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


def get_suitable_integration(integrations_data: list[dict], deal_city: str) -> dict:
    if len(integrations_data) > 1:
        suitable_integration = None
        for integration in integrations_data:
            suitable_integration = dict(integration)
            if (
                "МСК" in suitable_integration["sheet_name"] and deal_city == "Москва" or
                "МСК" not in suitable_integration["sheet_name"] and deal_city != "Москва"
            ):
                break
        return suitable_integration
    return integrations_data[0]


def handle_deal(deal_id: str):
    deal_info = get_deal_info(deal_id)
    integrations_data, integrations_exist = get_integrations_if_exist(deal_info.stage_id)
    if not integrations_exist:
        return
    suitable_integration = get_suitable_integration(integrations_data, deal_info.city)
    if deal_info.stage_id != suitable_integration["stage_id"]:
        if deal_info.stage_id in get_ids_for_invalid_stages(deal_info.stage_id):
            send_to_google_sheet(
                deal_info,
                settings.INVALID_LEADS_SHEET_ID,
                settings.INVALID_LEADS_SHEET_NAME,
            )
            send_message_to_tg(deal_info, settings.TG_INVALID_LEADS_CHAT)
        return
    if suitable_integration["previous_sheet_names"]:
        previous_sheet_names = str(suitable_integration["previous_sheet_names"]).split(", ")
    else:
        previous_sheet_names = []
    if is_unique_data(
            deal_info.phone,
            suitable_integration["google_spreadsheet_id"],
            suitable_integration["sheet_name"],
            previous_sheet_names,
    ):
        send_to_google_sheet(
            deal_info,
            suitable_integration["google_spreadsheet_id"],
            suitable_integration["sheet_name"],
        )
        send_message_to_tg(deal_info, suitable_integration["tg_bot_id"])
    else:
        move_deal_to_doubles_stage(deal_id, deal_info.stage_id)
