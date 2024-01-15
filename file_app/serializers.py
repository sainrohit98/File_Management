from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UploadedFile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','password']

    def create(self, validated_data):
        user = User.objects.create(email = validated_data['email'],password = validated_data['password'],username = validated_data['username'] )
        user.set_password(validated_data['password'])
        user.save()
        return validated_data
    
class UploadedFileSerializer(serializers.ModelSerializer):
    # user  = UserSerializer()
    class Meta:
        model = UploadedFile
        fields = '__all__'
