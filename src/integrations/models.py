from django.db import models


class IntegrationsData(models.Model):
    project_name = models.CharField(max_length=255)
    stage_id = models.CharField(max_length=255)
    tg_bot_id = models.CharField(max_length=255)
    google_spreadsheet_id = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255)
    previous_sheet_names = models.CharField(max_length=255, blank=True)


class ConfigProjectNames(models.Model):
    skorozvon_scenario_name = models.CharField(max_length=255)
    bitrix_project_name = models.CharField(max_length=255)


class FieldIds(models.Model):
    bitrix_field_name = models.CharField(max_length=255)
    bitrix_field_id = models.IntegerField()
    bitrix_field_value = models.CharField(max_length=255)


class CallDataInfo(models.Model):
    type = models.CharField(max_length=255)

    lead_id = models.IntegerField(null=True)
    lead_name = models.CharField(max_length=255)
    lead_comment = models.TextField(null=True, blank=True)
    lead_post = models.CharField(max_length=255, null=True, blank=True)
    lead_city = models.CharField(max_length=255, null=True, blank=True)
    lead_business = models.CharField(max_length=255, null=True, blank=True)
    lead_homepage = models.CharField(max_length=255, null=True, blank=True)
    lead_emails = models.JSONField(default=list)
    lead_inn = models.CharField(max_length=255, null=True, blank=True)
    lead_kpp = models.CharField(max_length=255, null=True, blank=True)
    lead_created_at = models.CharField(null=True)
    lead_updated_at = models.CharField(null=True)
    lead_deleted_at = models.CharField(null=True, blank=True)
    lead_parent_lead_id = models.IntegerField(null=True, blank=True)
    lead_tags = models.JSONField(default=list)
    lead_phones = models.CharField(max_length=255)

    contact_id = models.IntegerField(null=True)
    contact_name = models.CharField(max_length=255)
    contact_comment = models.TextField(null=True, blank=True)
    contact_post = models.CharField(max_length=255, null=True, blank=True)
    contact_city = models.CharField(max_length=255, null=True, blank=True)
    contact_business = models.CharField(max_length=255, null=True, blank=True)
    contact_homepage = models.CharField(max_length=255, null=True, blank=True)
    contact_emails = models.JSONField(default=list)
    contact_inn = models.CharField(max_length=255, null=True, blank=True)
    contact_kpp = models.CharField(max_length=255, null=True, blank=True)
    contact_created_at = models.CharField(null=True)
    contact_updated_at = models.CharField(null=True)
    contact_deleted_at = models.CharField(null=True, blank=True)
    contact_parent_lead_id = models.IntegerField(null=True)
    contact_tags = models.JSONField(default=list)
    contact_address = models.CharField(max_length=255, null=True, blank=True)
    contact_phones = models.CharField(max_length=255)

    call_id = models.IntegerField(null=True)
    call_phone = models.CharField(max_length=255)
    call_source = models.CharField(max_length=255)
    call_direction = models.CharField(max_length=255, )
    call_params = models.JSONField(default=dict)
    call_lead_id = models.IntegerField(null=True)
    call_organization_id = models.IntegerField(null=True)
    call_user_id = models.IntegerField(null=True)
    call_started_at = models.CharField(null=True)
    call_connected_at = models.CharField(null=True)
    call_ended_at = models.CharField(null=True)
    call_reason = models.CharField(max_length=255)
    call_duration = models.IntegerField(null=True)
    call_scenario_id = models.IntegerField(null=True)
    call_result_id = models.IntegerField(null=True)
    call_incoming_phone = models.CharField(max_length=255, null=True, blank=True)
    call_recording_url = models.URLField(null=True, blank=True)
    call_call_type = models.CharField(max_length=255)
    call_region = models.CharField(max_length=255)
    call_local_time = models.CharField(max_length=255)
    call_call_project_id = models.CharField(max_length=255)
    call_call_project_title = models.CharField(max_length=255)
    call_scenario_result_group_id = models.CharField(max_length=255)
    call_scenario_result_group_title = models.CharField(max_length=255)

    call_result_result_id = models.IntegerField(null=True)
    call_result_result_name = models.CharField(max_length=255)
    call_result_comment = models.TextField(null=True)
