# Generated by Django 5.0 on 2023-12-26 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0006_callinfo_scenario_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callinfo',
            name='comment',
            field=models.CharField(blank=True, null=True),
        ),
    ]
