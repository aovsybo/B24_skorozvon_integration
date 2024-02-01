from ..models import IntegrationsData, FieldIds
from ..api.serializers import IntegrationsDataSerializer, FieldIdsSerializer
from ..service.google_sheet_integration import get_sheet_config_data, get_funnel_info_from_integration_table

from apscheduler.schedulers.background import BackgroundScheduler


def get_spreadsheet_id_from_url(url: str):
    if url:
        return url.split("https://docs.google.com/spreadsheets/d/")[1].split("/")[0]
    return url


def get_tg_chat_id(chat_text: str):
    if ":" in chat_text and "\n" in chat_text:
        return chat_text.split("\n")[0].split(":")[1].strip()
    return chat_text


def check_for_null(value: str):
    if not value:
        return ""
    return value


def create_object(model_serializer, data: dict):
    serializer = model_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def sync_integrations_data(integrations_data: dict):
    for i in range(len(integrations_data["Проекты"])):
        if not integrations_data["Проекты"][i]:
            break
        if not integrations_data["ID Стадии"][i]:
            continue
        current_integration = {
            "project_name": integrations_data["Проекты"][i],
            "stage_id": integrations_data["ID Стадии"][i],
            "tg_bot_id": get_tg_chat_id(integrations_data["Телеграм бот:"][i]),
            "google_spreadsheet_id": get_spreadsheet_id_from_url(integrations_data["Ссылка на таблицу лидов [предыдущие]"][i]),
            "sheet_name": integrations_data["Название листа"][i],
            "previous_sheet_names": check_for_null(integrations_data["Названия прошлых листов"][i]),
            "skorozvon_scenario_name": check_for_null(integrations_data["Имя сценария в скорозвоне"][i]),
        }
        if IntegrationsData.objects.filter(project_name=current_integration["project_name"]).exists():
            instance = IntegrationsData.objects.get(project_name=current_integration["project_name"])
            serializer = IntegrationsDataSerializer(instance)
            for field in current_integration.keys():
                if current_integration[field] != serializer[field]:
                    serializer.update(instance, current_integration)
                    break
        else:
            create_object(IntegrationsDataSerializer, current_integration)


# def sync_project_names(project_names: dict):
#     for key, value in project_names.items():
#         data = {
#             "skorozvon_scenario_name": key,
#             "bitrix_project_name": value
#         }
#         if ConfigProjectNames.objects.filter(skorozvon_scenario_name=key).exists():
#             instance = ConfigProjectNames.objects.get(skorozvon_scenario_name=key)
#             serializer = ConfigProjectNamesSerializer(instance)
#             if key != serializer["skorozvon_scenario_name"] or value != serializer["bitrix_project_name"]:
#                 serializer.update(instance, data)
#         else:
#             create_object(ConfigProjectNamesSerializer, data)


def sync_field_ids(bitrix_field_name, config_data: dict):
    for field_id, field_value in config_data.items():
        data = {
            "bitrix_field_name": bitrix_field_name,
            "bitrix_field_id": field_id,
            "bitrix_field_value": field_value
        }
        if FieldIds.objects.filter(bitrix_field_name=bitrix_field_name).filter(bitrix_field_id=field_id).exists():
            instance = FieldIds.objects.get(bitrix_field_name=bitrix_field_name, bitrix_field_id=field_id)
            serializer = FieldIdsSerializer(instance)
            for key in data.keys():
                if data[key] != serializer[key]:
                    serializer.update(instance, data)
        else:
            create_object(FieldIdsSerializer, data)


def sync_google_sheets_data_to_db():
    sync_integrations_data(get_funnel_info_from_integration_table())
    sheet_config_data = get_sheet_config_data()
    # sync_project_names(sheet_config_data["Соответстиве имен сценариев и воронок"])
    for name, data in sheet_config_data.items():
        if name != "Соответстиве имен сценариев и воронок":
            sync_field_ids(name, data)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_google_sheets_data_to_db, 'cron', second="1")
    scheduler.start()
