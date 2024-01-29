from rest_framework import serializers

from ..models import CallDataInfo


class CallDataInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallDataInfo
        fields = '__all__'
