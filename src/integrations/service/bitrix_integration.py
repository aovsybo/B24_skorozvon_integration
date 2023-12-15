import requests

from django.conf import settings


def get_deal_info():
    fields = requests.get(settings.BITRIX_GET_DEAL_API_URL).json()["result"]
    last_deal = fields[-1]
    response = {}
    for header in settings.REQUEST_FIELDS:
        response[header] = last_deal[header]
    return response


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


def get_current_contact_id(lead_name, call_phone):
    create_contact(lead_name, call_phone)
    response = requests.get(url=settings.BITRIX_GET_LIST_OF_CONTACTS)
    contacts = response.json()["result"]
    current_contact = max(contacts, key=lambda x: x["ID"])
    return current_contact["ID"]


def create_bitrix_deal(deal_name, lead_name, call_phone, lead_comment, share_link):
    current_contact_id = get_current_contact_id(lead_name, call_phone)
    data = {
        "fields": {
            "TITLE": deal_name,
            "COMMENTS": f"Запись разговора: {share_link}\n"
                        f"Комментарий: {lead_comment}",
            "CONTACT_ID": current_contact_id
        }
    }
    response = requests.post(url=settings.BITRIX_CREATE_DEAL_API_LINK, json=data)
    return {
        "status": response.status_code,
        "message": response.text
    }