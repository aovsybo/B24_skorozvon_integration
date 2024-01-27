import requests

from django.conf import settings

from .google_sheet_integration import get_config_sheet_data
from .skorozvon_integration import skorozvon_api
from .yandex_disk_integration import get_file_share_link


def convert_date_to_ru(date: str):
    return ".".join(date.split("T")[0].split("-")[::-1])


def unify_phone(phone: str):
    # Приводим номер к единому формату
    replace_symbols = "+-_() "
    for replace_symbol in replace_symbols:
        phone = phone.replace(replace_symbol, "")
    if phone:
        return f"7{phone[::-1][:10][::-1]}"
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
        # "lead_type": get_config_sheet_data("Тип лида", deal["UF_CRM_1664819174514"]),
        "lead_type": settings.BITRIX_LEAD_TYPE[deal["UF_CRM_1664819174514"]],
        # "lead_qualification": get_config_sheet_data("Квалификация лида", deal["UF_CRM_1664819117290"]),
        "lead_qualification": settings.BITRIX_LEAD_QUALIFICATION[deal["UF_CRM_1664819117290"]],
        "lead_comment": deal["UF_CRM_1664819040131"],
        "link_to_audio": deal["UF_CRM_1664819217017"],
        "date": convert_date_to_ru(deal["DATE_MODIFY"]),
        "city": settings.BITRIX_CITIES[deal["UF_CRM_1687464323171"]],
        # "city": get_config_sheet_data("Город", deal["UF_CRM_1687464323171"]),
        "country": settings.BITRIX_COUNTRIES[deal["UF_CRM_1688409961271"]],
        # "country": get_config_sheet_data("Страна", deal["UF_CRM_1688409961271"]),
        "car_mark": deal["UF_CRM_1694678311862"],
        "car_model": deal["UF_CRM_1694678343732"],
    }
    return response, deal["STAGE_ID"]


def create_contact(lead_name, call_phone):
    data = {
        "fields": {
            "NAME": lead_name,
            "PHONE": [call_phone]
        }
    }
    create_status = requests.post(url=settings.BITRIX_CREATE_CONTACT_API_LINK, json=data)
    if create_status == 200:
        return {"status": "success"}
    else:
        return {"status": "failed"}


def get_contacts_list():
    return requests.get(url=settings.BITRIX_GET_LIST_OF_CONTACTS).json()["result"]


def get_or_create_contact_id(lead_name, call_phone):
    contacts = get_contacts_list()
    create_contact(lead_name, call_phone)
    current_contact = max(contacts, key=lambda x: x["ID"])
    return current_contact["ID"]


def create_bitrix_deal(lead_info: dict):
    # TODO: set timer
    call_id = lead_info.get("call_id", "")
    call_data = skorozvon_api.get_call_audio(call_id)
    share_link = get_file_share_link(call_data, call_id)
    # TODO: bitrix creation
    # current_contact_id = get_or_create_contact_id(lead_name, call_phone)
    data = {
        "fields": {
            "TITLE": "Лид",
            "COMMENTS": f"Запись разговора: {share_link}\n"
                        f"Комментарий: {lead_info['comment']}",
            # TODO: Брать айди категории от сценария
            "CATEGORY_ID": "94"
        }
    }
    response = requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)
    return {
        "status": response.status_code,
        "message": response.text,
        "response": response.json(),
    }


def get_category_id(category_name):
    response = requests.get(settings.BITRIX_GET_DEAL_CATEGORY_LIST)
    categories = response.json()["result"]
    for category in categories:
        if category["NAME"] == category_name:
            return category["ID"]
    return 0
