# Generated by Django 5.0 on 2023-12-14 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0002_rename_contact_id_callinfo_organisation_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callinfo',
            name='organisation_phone',
            field=models.CharField(max_length=20),
        ),
    ]
