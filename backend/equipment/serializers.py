from rest_framework import serializers
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    equipments = EquipmentSerializer(many=True, read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'uploaded_at', 'uploaded_by_username', 'file', 
                  'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipments']
        read_only_fields = ['uploaded_at', 'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Serializer for dataset list without equipment details"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'uploaded_at', 'uploaded_by_username', 
                  'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
