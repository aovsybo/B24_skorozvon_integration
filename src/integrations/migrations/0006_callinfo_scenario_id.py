# Generated by Django 5.0 on 2023-12-25 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0005_remove_callinfo_yandex_disk_link_callinfo_call_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='callinfo',
            name='scenario_id',
            field=models.CharField(default='0'),
            preserve_default=False,
        ),
    ]