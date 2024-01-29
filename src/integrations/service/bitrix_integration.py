from functools import wraps
import requests
import time

from django.conf import settings

from .google_sheet_integration import get_config_sheet_data
from .skorozvon_integration import skorozvon_api
from .yandex_disk_integration import get_file_share_link
from .telegram_integration import send_message_to_dev_chat


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


def get_deal_info(deal_id):
    deal = requests.get(settings.BITRIX_GET_DEAL_BY_ID, params={"ID": deal_id}).json()["result"]
    response = {
        "lead_name": deal["UF_CRM_1664819061161"],
        "phone": unify_phone(deal["UF_CRM_1665719874029"]),
        "lead_type": settings.BITRIX_LEAD_TYPE[deal["UF_CRM_1664819174514"]],
        "lead_qualification": settings.BITRIX_LEAD_QUALIFICATION[deal["UF_CRM_1664819117290"]],
        "lead_comment": deal["UF_CRM_1664819040131"],
        "link_to_audio": deal["UF_CRM_1664819217017"],
        "date": convert_date_to_ru(deal["DATE_MODIFY"]),
        "city": settings.BITRIX_CITIES[deal["UF_CRM_1687464323171"]],
        "country": settings.BITRIX_COUNTRIES[deal["UF_CRM_1688409961271"]],
        "car_mark": deal["UF_CRM_1694678311862"],
        "car_model": deal["UF_CRM_1694678343732"],
    }
    return response, deal["STAGE_ID"]


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
def create_bitrix_deal(lead_info: dict):
    call_id = lead_info.get("call_id", "")
    call_data = skorozvon_api.get_call_audio(call_id)
    share_link = get_file_share_link(call_data, call_id)
    data = {
        "fields": {
            "TITLE": "Лид",
            "UF_CRM_1665719874029": lead_info['organisation_name'],
            "UF_CRM_1664819061161": lead_info['organisation_phone'],
            "UF_CRM_1664819217017": share_link,
            "UF_CRM_1664819040131": lead_info['comment'],
            # TODO: Брать айди категории от сценария
            "CATEGORY_ID": "94",
        }
    }
    return requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)


def get_category_id(category_name):
    response = requests.get(settings.BITRIX_GET_DEAL_CATEGORY_LIST)
    categories = response.json()["result"]
    for category in categories:
        if category["NAME"] == category_name:
            return category["ID"]
    return 0
