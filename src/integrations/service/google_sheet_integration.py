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


def get_table_data_by_range(table_link, sheet_name, sheet_range):
    """
    Получаем данные из таблицы по ссылке и имени листа
    """
    service = get_service()
    response = service.spreadsheets().values().get(
        spreadsheetId=table_link,
        range=f"{sheet_name}!{sheet_range}"
    ).execute()
    return response["values"]


def get_funnel_info_from_integration_table():
    """
    Получаем данные из таблицы с интеграциями по названию интеграции
    """
    table = get_table_data(settings.INTEGRATIONS_SPREADSHEET_ID, settings.INTEGRATIONS_SHEET_NAME)
    df = pd.DataFrame(table[2:], columns=table[1])
    request_columns = [
        'Проекты',
        'ID Стадии',
        'Ссылка на таблицу лидов [предыдущие]',
        'Название листа',
        'Названия прошлых листов',
        'Телеграм бот:'
    ]
    return df[request_columns]


def validate_data(fields: dict, stage_id: str):
    """
    Приводим данные к форме для записи в гугл таблицу
    Для некоторых вороноке обозначены свои формы
    """
    if stage_id in ["C21:EXECUTING", "C37:EXECUTING"]:
        # Для [П5]
        insert_data = [
            fields['date'],
            "",  ## для записи вручную
            fields['phone'],
            fields['city'],
            f"Имя: {fields['lead_name']}. Комментарий: {fields['lead_comment']}",
            fields['link_to_audio'],
        ]
    elif stage_id == "C17:EXECUTING":
        # Для [П15]
        insert_data = [
            fields['date'],
            "",  ## для записи вручную
            fields['phone'],
            f"Имя: {fields['lead_name']}. Комментарий: {fields['lead_comment']}",
            fields['link_to_audio'],
            fields['country'],
        ]
    elif stage_id == "C13:EXECUTING":
        # Для [П17]
        insert_data = [
            fields['date'],
            "",  ## для записи вручную
            fields['phone'],
            fields['car_mark'],
            fields['car_model'],
            f"Имя: {fields['lead_name']}. Комментарий: {fields['lead_comment']}",
            fields['link_to_audio'],
        ]
    else:
        # Для остальных
        insert_data = [
            fields['date'],
            "", ## для записи вручную
            fields['lead_name'],
            fields['phone'],
            fields['lead_comment'],
            f"{fields['lead_type']} | {fields['lead_qualification']}",
            fields['link_to_audio'],
        ]
    return insert_data


def is_unique_data(phone: str, table_link: str, sheet_name: str, previous_sheet_names: list[str]):
    """
    Проверям, нет ли лида с таким номером в листах данной таблицы
    """
    all_sheet_names = [sheet_name] + previous_sheet_names
    phone_id = -1
    for current_sheet_name in all_sheet_names:
        funnel_table = get_table_data(table_link, current_sheet_name)
        for field_name in funnel_table[0]:
            if field_name in settings.PHONE_FIELD_NAMES:
                phone_id = funnel_table[0].index(field_name)
                break
        if phone_id == -1:
            send_message_to_dev(f"Не найдено поле с телефоном в таблице {table_link}")
            return True
        if phone in [deal_info[phone_id].strip() for deal_info in funnel_table[1:] if deal_info]:
            return False
    return True


def send_to_google_sheet(data: dict, stage_id: str, spreadsheet_id: str, sheet_name: str):
    """
    Отправляем данные в гугл таблицу по указанному айди таблицы и названию листа
    """
    service = get_service()
    body = {
        "values": [validate_data(data, stage_id)]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:{len(data)}",
        valueInputOption="USER_ENTERED", body=body).execute()
    return result


def get_table_url_from_link(url: str):
    return url.split("https://docs.google.com/spreadsheets/d/")[1].split("/")[0]


def get_funnel_table_links(stage_id: str, integrations_table, city: str):
    """
    Получаем данные таблицы по ID стадии
    """
    links = integrations_table.loc[integrations_table['ID Стадии'] == stage_id].to_dict("records")
    count_of_integrations = len(links)
    funnel_number = links[0]["Проекты"].split()[0]
    index = 0
    if count_of_integrations > 1 and funnel_number == "[П5]":
        # Если работаем с воронкой П5 где более одной записи, то имя листа получаем по городу
        for i, link in enumerate(links):
            # получаем нужный индекс записи по слову "МСК" если искомый лист - московский,
            # и по отстутствию слова "МСК" если искомый - по РФ
            is_msk = city == "Москва"
            sheet_name = link["Название листа"]
            if "МСК" in sheet_name and is_msk or "МСК" not in sheet_name and not is_msk:
                index = i
                break
    previous_sheet_names = []
    if links[index]["Названия прошлых листов"]:
        previous_sheet_names = links[index]["Названия прошлых листов"].split(', ')
    return {
        "tg": links[index]["Телеграм бот:"].split("\n\n")[0].split(":")[1].strip(),
        "table_link": get_table_url_from_link(links[index]["Ссылка на таблицу лидов [предыдущие]"]),
        "sheet_name": links[index]["Название листа"],
        "previous_sheet_names": previous_sheet_names,
    }


def get_config_sheet_data(column: str, code: str):
    i = settings.CONFIG_SHEET_FIELDS.index(column) * 2
    sheet_range = f"{chr(ord('A') + i)}:{chr(ord('A') + i + 1)}"
    table = get_table_data_by_range(settings.INTEGRATIONS_SPREADSHEET_ID, settings.CONFIG_SHEET_NAME, sheet_range)
    for pair in table[2:]:
        if pair[0] == code:
            return pair[1]
    return ""
