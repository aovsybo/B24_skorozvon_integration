from ..models import FieldIds, IntegrationsData, ScenarioIds, FormFieldIds
from ..api.serializers import IntegrationsDataSerializer
from .exceptions import CategoryNotFoundError, ScenarioNotFoundError


def get_category_id(scenario_id):
    try:
        scenario = ScenarioIds.objects.get(scenario_id=scenario_id)
        searching_field = ScenarioIds._meta.get_field("scenario_name")
        scenario_name = getattr(scenario, searching_field.attname)
    except ScenarioIds.DoesNotExist:
        raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
    try:
        integration = IntegrationsData.objects.get(skorozvon_scenario_name=scenario_name)
        searching_field = IntegrationsData._meta.get_field("stage_id")
        stage_id = getattr(integration, searching_field.attname)
    except IntegrationsData.DoesNotExist:
        raise CategoryNotFoundError(f"Not found category according to scenario '{scenario_name}'")
    return stage_id.split(":")[0].strip("C") if ":" in stage_id else stage_id


def get_field_value_by_id(field_name: str, field_id: str) -> str:
    if field_id == "":
        return ""
    try:
        field_pair = FieldIds.objects.get(bitrix_field_name=field_name, bitrix_field_id=field_id)
        field_object = FieldIds._meta.get_field("bitrix_field_value")
        field_value = getattr(field_pair, field_object.attname)
    except FieldIds.DoesNotExist:
        field_value = ""
    return field_value


def get_integrations_if_exist(stage_id: str) -> (list[dict], bool):
    integration_by_stage_id = IntegrationsData.objects.filter(stage_id=stage_id)
    integrations_exist = integration_by_stage_id.exists()
    if not integrations_exist:
        return [], False
    integrations_data = IntegrationsDataSerializer(
        integration_by_stage_id,
        many=True
    )
    return integrations_data.data, integrations_exist


def get_form_field_id_by_form_field_name(field_name: str) -> str:
    if FormFieldIds.objects.filter(field_name__iexact=field_name).exists():
        instance = FormFieldIds.objects.get(field_name__iexact=field_name)
        searching_field = FormFieldIds._meta.get_field("field_id")
        return getattr(instance, searching_field.attname)
    return ""


def get_bitrix_field_id(question, answer):
    if FieldIds.objects.filter(bitrix_field_name__iexact=question, bitrix_field_value__iexact=answer).exists():
        instance = FieldIds.objects.get(bitrix_field_name__iexact=question, bitrix_field_value__iexact=answer)
        searching_field = FieldIds._meta.get_field("bitrix_field_id")
        return getattr(instance, searching_field.attname)
    return answer


def get_project_name_by_stage_id(stage_id: str) -> str:
    if IntegrationsData.objects.filter(stage_id=stage_id).exists():
        instance = IntegrationsData.objects.get(stage_id=stage_id)
        searching_field = IntegrationsData._meta.get_field("project_name")
        return getattr(instance, searching_field.attname)
    return "Ошибка получения проекта"
