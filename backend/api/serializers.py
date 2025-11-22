from rest_framework import serializers
from .models import Dataset
class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id','name','upload_time','file','row_count','checksum']
