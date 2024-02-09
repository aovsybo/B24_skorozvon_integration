# Generated by Django 5.0 on 2024-02-09 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0013_delete_configprojectnames_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_connected_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_ended_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_lead_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_organization_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_result_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_result_result_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_scenario_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_started_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='call_user_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_created_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_deleted_at',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_id',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_parent_lead_id',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_phones',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='contact_updated_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='lead_created_at',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='lead_deleted_at',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='lead_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='lead_parent_lead_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calldatainfo',
            name='lead_updated_at',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
