# Generated by Django 5.0 on 2023-12-14 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='callinfo',
            old_name='contact_id',
            new_name='organisation_phone',
        ),
    ]
