# Generated by Django 5.0 on 2024-01-29 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0007_alter_callinfo_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CallInfo',
        ),
    ]
