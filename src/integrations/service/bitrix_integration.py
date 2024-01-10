import requests

from django.conf import settings


def convert_date_to_ru(date: str):
    return ".".join(date.split("T")[0].split("-")[::-1])


def unify_phone(phone: str):
    # Приводим номер к единому формату
    if phone:
        return f"7{phone[::-1][:10][::-1]}"
    return phone


def get_deal_info(deal_id):
    deal = requests.get(settings.BITRIX_GET_DEAL_BY_ID, params={"ID": deal_id}).json()["result"]
    response = {
        "lead_name": deal["UF_CRM_1664819061161"],
        "phone": unify_phone(deal["UF_CRM_1665719874029"]),
        "lead_type": deal["UF_CRM_1664819174514"],
        "lead_qualification": deal["UF_CRM_1664819117290"],
        "lead_comment": deal["UF_CRM_1664819040131"],
        "link_to_audio": deal["UF_CRM_1664819217017"],
        "date": convert_date_to_ru(deal["DATE_MODIFY"]),
        "city": "",
        "country": "",
        "car_mark": "",
        "car_model": "",
    }
    extra_fields = {
        "city": {
            "has_choices": True,
            "code": "UF_CRM_1687464323171",
            "id_to_name": settings.BITRIX_CITIES,
        },
        "country": {
            "has_choices": True,
            "code": "UF_CRM_1688409961271",
            "id_to_name": settings.BITRIX_COUNTRIES,
        },
        "car_mark": {
            "has_choices": False,
            "code": "UF_CRM_1694678311862",
        },
        "car_model": {
            "has_choices": False,
            "code": "UF_CRM_1694678343732",
        },
    }
    for field, info in extra_fields.items():
        if info["code"] in deal and deal[info["code"]]:
            if info["has_choices"]:
                response[field] = info["id_to_name"][deal[info["code"]]]
            else:
                response[field] = deal[info["code"]]
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


def create_bitrix_deal(deal_name, lead_name, call_phone, lead_comment, share_link, category_id):
    current_contact_id = get_or_create_contact_id(lead_name, call_phone)
    data = {
        "fields": {
            "TITLE": deal_name,
            "COMMENTS": f"Запись разговора: {share_link}\n"
                        f"Комментарий: {lead_comment}",
            "CONTACT_ID": current_contact_id,
            "CATEGORY_ID": category_id
        }
    }
    response = requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)
    return {
        "status": response.status_code,
        "message": response.text
    }


def get_category_id(category_name):
    response = requests.get(settings.BITRIX_GET_DEAL_CATEGORY)
    categories = response.json()["result"]
    for category in categories:
        if category["NAME"] == category_name:
            return category["ID"]
    return 0
