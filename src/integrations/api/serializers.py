from rest_framework import serializers

from ..models import CallDataInfo, IntegrationsData, FieldIds, ScenarioIds


class FieldIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldIds
        fields = '__all__'


class IntegrationsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationsData
        fields = '__all__'


class CallDataInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallDataInfo
        fields = '__all__'


class ScenarioIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioIds
        fields = '__all__'
