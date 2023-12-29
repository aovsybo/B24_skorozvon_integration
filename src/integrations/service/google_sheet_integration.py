import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from django.conf import settings


def get_service():
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


def get_table_data():
    service = get_service()
    response = service.spreadsheets().values().get(
        spreadsheetId=settings.INTEGRATIONS_SPREADSHEET_ID,
        range="Лист1"
    ).execute()
    return response["values"]


def validate_data(fields: dict):
    insert_data = [
        f"{fields['lead_name']}_{fields['phone']}",
        fields['lead_name'],
        fields['phone'],
        fields['lead_comment'],
        f"{fields['lead_type']} | {fields['lead_qualification']}",
        fields['link_to_audio'],
        fields['date'],
    ]
    return insert_data


def is_unique_data(fields: dict):
    table = get_table_data()
    insert_data = validate_data(fields)
    return f"{table}, {insert_data}"


def send_to_google_sheet(fields: dict, spreadsheet_id: str):
    service = get_service()
    body = {
        "values": [validate_data(fields)]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=f"Лист1!1:{len(fields)}",
        valueInputOption="RAW", body=body).execute()
    return result


def get_table(funnel):
    table = get_table_data()
    integration = list(filter(lambda x: x[0] == funnel, table))
    integration_data = {
            "tg": "",
            "table_link": ""
        }
    if integration:
        integration_data["tg"] = integration[0][1]
        integration_data["sheets"] = integration[0][2].split(
            "https://docs.google.com/spreadsheets/d/"
        )[1].split("/")[0]
    return integration_data


def get_funnel_names():
    table = get_table_data()
    funnel_names = [integration[0] for integration in table[1:]]
    return funnel_names
