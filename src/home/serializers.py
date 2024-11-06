from rest_framework import serializers
from .models import LogEntry,Host,Level,RequestMethod



class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        exclude = ['added_now', 'update_now']
        
class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        exclude = ['added_now', 'update_now']

class RequestMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMethod
        exclude = ['added_now', 'update_now']

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        exclude = ['added_now']
