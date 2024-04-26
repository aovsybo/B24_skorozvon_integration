import os
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from django.conf import settings

from .telegram_integration import send_message_to_dev
from .validation import BitrixDeal, Integration


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


def get_sheet_config_data():
    """
    Функция возвращает данные с листа конфигурации
    в формате название таблицы: {поле: значение, поле: значение}
    """
    config_data = dict()
    config_sheet_data = get_table_data(
        settings.INTEGRATIONS_SPREADSHEET_ID,
        settings.CONFIG_SHEET_NAME,
    )
    for i, name in enumerate([config_header for config_header in config_sheet_data[0] if config_header]):
        config_data[name] = {
            line[0+i*2]: line[1+i*2]
            for line in config_sheet_data[2:]
            if len(line) > i*2 and line[0+i*2]
        }
    return config_data


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
        'Статус',
        'ID Стадии',
        'Ссылка на таблицу лидов [предыдущие]',
        'Название листа',
        'Названия прошлых листов',
        'Телеграм бот:',
        'Имя сценария в скорозвоне',
    ]
    return df[request_columns]


def insert_data_by_stage(deal_info: BitrixDeal):
    """
    Приводим данные к форме для записи в гугл таблицу
    Для некоторых вороноке обозначены свои формы
    """
    if not deal_info.is_valid_lead:
        insert_data = [
            deal_info.date,
            "",  ## для записи вручную
            deal_info.project_name,
            deal_info.link_to_lead,
            deal_info.lead_name,
            deal_info.phone,
            f"Имя: {deal_info.lead_name}. Комментарий: {deal_info.lead_comment}",
            f"{deal_info.lead_type} | {deal_info.lead_qualification}",
            deal_info.link_to_audio,
        ]
    elif deal_info.stage_id in ["C21:EXECUTING", "C37:EXECUTING"]:
        # Для [П5]
        insert_data = [
            deal_info.date,
            "",  ## для записи вручную
            deal_info.phone,
            deal_info.city,
            f"Имя: {deal_info.lead_name}. Комментарий: {deal_info.lead_comment}",
            deal_info.link_to_audio,
        ]
    elif deal_info.stage_id == "C17:EXECUTING":
        # Для [П15]
        insert_data = [
            deal_info.date,
            "",  ## для записи вручную
            deal_info.phone,
            f"Имя: {deal_info.lead_name}. Комментарий: {deal_info.lead_comment}",
            deal_info.link_to_audio,
            deal_info.country,
        ]
    elif deal_info.stage_id == "C13:EXECUTING":
        # Для [П17]
        insert_data = [
            deal_info.date,
            "",  ## для записи вручную
            deal_info.phone,
            deal_info.car_mark,
            deal_info.car_model,
            f"Имя: {deal_info.lead_name}. Комментарий: {deal_info.lead_comment}",
            deal_info.link_to_audio,
        ]
    else:
        # Для остальных
        insert_data = [
            deal_info.date,
            "", ## для записи вручную
            deal_info.lead_name,
            deal_info.phone,
            deal_info.lead_comment,
            f"{deal_info.lead_type} | {deal_info.lead_qualification}",
            deal_info.link_to_audio,
        ]
    return insert_data


def is_unique_data(phone: str, integration: Integration):
    """
    Проверям, нет ли лида с таким номером в листах данной таблицы
    """
    all_sheet_names = [integration.sheet_name] + integration.previous_sheet_names
    phone_id = -1
    for current_sheet_name in all_sheet_names:
        funnel_table = get_table_data(integration.google_spreadsheet_id, current_sheet_name)
        for field_name in funnel_table[0]:
            if field_name in settings.PHONE_FIELD_NAMES:
                phone_id = funnel_table[0].index(field_name)
                break
        if phone_id == -1:
            send_message_to_dev(f"Не найдено поле с телефоном в таблице {integration.table_link}")
            return True
        if phone in [deal_info[phone_id].strip() for deal_info in funnel_table[1:] if deal_info]:
            return False
    return True


def send_to_google_sheet(deal_info: BitrixDeal, integration: Integration):
    """
    Отправляем данные в гугл таблицу по указанному айди таблицы и названию листа
    """
    service = get_service()
    insert_data = insert_data_by_stage(deal_info)
    body = {
        "values": [insert_data]
    }
    try:
        return service.spreadsheets().values().append(
            spreadsheetId=integration.google_spreadsheet_id,
            range=f"{integration.sheet_name}!1:{len(insert_data)}",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
    except Exception as e:
        send_message_to_dev(f"Ошибка отправки лида в таблицу: {deal_info.link_to_lead}")



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


invalid_integration = Integration(
    tg_bot_id=settings.TG_INVALID_LEADS_CHAT,
    google_spreadsheet_id=settings.INVALID_LEADS_SHEET_ID,
    sheet_name=settings.INVALID_LEADS_SHEET_NAME,
)
