# Generated by Django 5.0 on 2024-01-31 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0010_configprojectsname_fieldids_integrationsdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldids',
            name='bitrix_field_value',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]