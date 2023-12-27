import requests

from django.conf import settings


def get_deal_info(deal_id):
    deal = requests.get(settings.BITRIX_GET_DEAL_BY_ID, params={"ID": deal_id}).json()["result"]
    response = dict()
    response["phone"] = ("Телефон", deal["UF_CRM_1665719874029"])
    response["lead_name"] = ("Имя лида", deal["UF_CRM_1664819061161"])
    response["lead_type"] = ("Тип лида", deal["UF_CRM_1664819174514"])
    response["lead_qualification"] = ("Квалификаций лида", deal["UF_CRM_1664819117290"])
    response["lead_comment"] = ("Комментарий к лиду", deal["UF_CRM_1664819040131"])
    response["link_to_audio"] = ("Ссылка на аудиозапись[актуальная]", deal["UF_CRM_1664819217017"])
    return response, deal["CATEGORY_ID"]


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


def get_or_create_contact_id(lead_name, call_phone):
    response = requests.get(url=settings.BITRIX_GET_LIST_OF_CONTACTS)
    contacts = response.json()["result"]
    # filter(lambda person: person['name'] == 'Pam', people)
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
