import os
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from django.conf import settings

from .telegram_integration import send_message_to_dev

def get_service():
    """
    Получам доступ к гугл таблицам
    """
    creds = None
    if os.path.exists(settings.BASE_DIR / "token.json"):
        creds = Credentials.from_authorized_user_file(settings.BASE_DIR / "token.json", settings.SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.BASE_DIR / "credentials.json", settings.SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(settings.BASE_DIR / "token.json", "w") as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)


def get_table_data(table_link, sheet_name):
    """
    Получаем данные из таблицы по ссылке и имени листа
    """
    service = get_service()
    response = service.spreadsheets().values().get(
        spreadsheetId=table_link,
        range=sheet_name
    ).execute()
    return response["values"]


def get_funnel_info_from_integration_table():
    """
    Получаем данные из таблицы с интеграциями по названию интеграции
    """
    table = get_table_data(settings.INTEGRATIONS_SPREADSHEET_ID, settings.INTEGRATIONS_SHEET_NAME)
    df = pd.DataFrame(table[2:], columns=table[1])
    request_columns = [
        'Все проекты на 13.12',
        'ID Стадии',
        'Ссылка на таблицу лидов [предыдущие]',
        'Название листа',
        'Телеграм бот:'
    ]
    return df[request_columns]


def validate_data(fields: dict):
    """
    Приводим данные к форме для записи в гугл таблицу
    """
    lead_type = settings.BITRIX_LEAD_TYPE[fields['lead_type']]
    lead_qualification = settings.BITRIX_LEAD_QUALIFICATION[fields['lead_qualification']]
    insert_data = [
        fields['date'],
        "", ## для записи вручную
        fields['lead_name'],
        fields['phone'],
        fields['lead_comment'],
        f"{lead_type} | {lead_qualification}",
        fields['link_to_audio'],
    ]
    return insert_data


def is_unique_data(data: dict, table_link: str, sheet_name: str):
    """
    Проверям, нет ли таких данных, записанных в таблицу c указанным stage_id
    """
    insert_data = validate_data(data)
    funnel_table = get_table_data(table_link, sheet_name)
    return insert_data not in funnel_table


def send_to_google_sheet(data: dict, spreadsheet_id: str, sheet_name: str):
    """
    Отправляем данные в гугл таблицу по указанному айди таблицы и названию листа
    """
    service = get_service()
    body = {
        "values": [validate_data(data)]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:{len(data)}",
        valueInputOption="RAW", body=body).execute()
    return result


def get_table_url_from_link(url: str):
    return url.split(
            "https://docs.google.com/spreadsheets/d/"
        )[1].split("/")[0]


def get_funnel_table_links(stage_id: str, integrations_table, is_msk: bool = False):
    """
    Получаем данные таблицы по ID стадии
    """
    # TODO: Некоторые воронки имеют более одной таблицы по айди, учесть
    links = integrations_table.loc[integrations_table['ID Стадии'] == stage_id].to_dict()
    count_of_integrations = len(links["Ссылка на таблицу лидов [предыдущие]"])
    index = 0
    if count_of_integrations > 1:
        for i, sheet_name in links["Название листа"].items():
            # получаем нужный индекс записи по слову "МСК" если искомый лист - московский,
            # и по отстутствию слова "МСК" если искомый - по РФ
            if "МСК" in sheet_name and is_msk or "МСК" not in sheet_name and not is_msk:
                index = i
                break
    return {
            "tg": links["Телеграм бот:"][index].split("\n\n")[0].split(":")[1].strip(),
            "table_link": get_table_url_from_link(links["Ссылка на таблицу лидов [предыдущие]"][index]),
            "sheet_name": links["Название листа"][index],
        }
