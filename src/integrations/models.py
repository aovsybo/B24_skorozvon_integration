from django.db import models


class CallInfo(models.Model):
    organisation_name = models.CharField(max_length=255)
    organisation_phone = models.CharField(max_length=20)
    comment = models.CharField()
    yandex_disk_link = models.TextField()
