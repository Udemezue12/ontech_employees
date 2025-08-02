from .models import WebAuthnCredential
import base64
from rest_framework import serializers
from django.contrib.auth import authenticate
# from django.contrib.auth import get_user_model
from .models import *


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'role', 'email', 'department',
                  'username', 'name', 'phone_number']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        ret['id'] = instance.id
        return ret



class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'phone_number',
                  'email', 'password', 'role', "department"]
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {'error_messages': {'unique': 'This email is already registered.'}},
            'username': {'error_messages': {'unique': 'This username is taken.'}},
            'phone_number': {
                'error_messages': {'unique': 'This phone number is already registered.'}
            },
           

        }
  

    def create(self, validated_data):
        
        role = validated_data.get('role')
        user = CustomUser.objects.create_user(**validated_data)

        user.save()
        return user


class HrManagerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'phone_number',
                  'email', 'password', 'role', "department"]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},
            'email': {'error_messages': {'unique': 'This email is already registered.'}},
            'username': {'error_messages': {'unique': 'This username is taken.'}},
            'phone_number': {'error_messages': {'unique': 'This phone number is already registered.'}},
        }

 
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'Hr_Manager'
        # validated_data['department'] = 'Human Resources'
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user




class ManagerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'phone_number',
                  'email', 'password', 'role', "department"]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},
            'email': {'error_messages': {'unique': 'This email is already registered.'}},
            'username': {'error_messages': {'unique': 'This username is taken.'}},
            'phone_number': {'error_messages': {'unique': 'This phone number is already registered.'}},
        }

   

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'Manager'
        
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class EmployeeRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'phone_number',
                  'email', 'password', 'role', "department"]
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'role': {'read_only': True},
            'email': {'error_messages': {'unique': 'This email is already registered.'}},
            'username': {'error_messages': {'unique': 'This username is taken.'}},
            'phone_number': {
                'error_messages': {'unique': 'This phone number is already registered.'}
            },
          

        }



    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'Employee'
        
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class OverallAdminRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'phone_number',
                  'email', 'password', 'role', "department"]
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'role': {'read_only': True},
            'email': {'error_messages': {'unique': 'This email is already registered.'}},
            'username': {'error_messages': {'unique': 'This username is taken.'}},
            'phone_number': {
                'error_messages': {'unique': 'This phone number is already registered.'}
            },
       

        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'Overall_Admin'
       
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class CreateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']


class ViewProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
       


class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['personal_details', 'country', 'state', 'resume', 'picture']
        read_only_fields = ['user']


class WebAuthnCredentialCreateSerializer(serializers.ModelSerializer):
    device_fingerprint = serializers.CharField(write_only=True)
    public_key = serializers.CharField(
        write_only=True) 

    class Meta:
        model = WebAuthnCredential
        fields = [
            'id', 'user', 'credential_id', 'public_key',
            'counter', 'device_fingerprint'
        ]
        read_only_fields = ['id', 'user',
                            'counter', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        credential_id = attrs.get('credential_id')
        public_key_b64 = attrs.get('public_key')
        device_fingerprint = attrs.get('device_fingerprint')

        try:
            public_key_bytes = base64.b64decode(public_key_b64)
            
        except Exception:
            raise serializers.ValidationError("Invalid public key format")

    
        if WebAuthnCredential.objects.filter(user=user, credential_id=credential_id).exists():
            raise serializers.ValidationError(
                "This credential ID is already registered for this user.")

        
        if WebAuthnCredential.objects.filter(user=user, public_key=public_key_bytes).exists():
            raise serializers.ValidationError(
                "This public key is already registered for this user.")

       
        if WebAuthnCredential.objects.filter(device_fingerprint=device_fingerprint).exclude(user=user).exists():
            raise serializers.ValidationError(
                "This fingerprint is already registered with another account.")

        return attrs

    def create(self, validated_data):
        validated_data['public_key'] = base64.b64decode(
            validated_data['public_key'])

        return WebAuthnCredential.objects.create(
            user=self.context['request'].user,
            credential_id=validated_data['credential_id'],
            public_key=validated_data['public_key'],
            device_fingerprint=validated_data['device_fingerprint'],
        )


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class ManualAttendanceSerializer(serializers.ModelSerializer):
    can_check_out = serializers.SerializerMethodField()
    should_show_check_in = serializers.SerializerMethodField()
    should_show_check_out = serializers.SerializerMethodField()

    class Meta:
        model = ManualAttendance
        fields = '__all__'

    def get_can_check_out(self, obj):
        return obj.can_check_out()

    def get_should_show_check_in(self, obj):
        return obj.should_show_check_in()

    def get_should_show_check_out(self, obj):
        return obj.should_show_check_out()


class BiometricAttendanceSerializer(serializers.ModelSerializer):
    can_check_out = serializers.SerializerMethodField()
    can_check_in = serializers.SerializerMethodField()
    overtime_hours = serializers.SerializerMethodField()
    check_in_time = serializers.SerializerMethodField()

    class Meta:
        model = BiometricAttendance
        fields = [
            "id", "date", "check_in", "check_out", "worked_hours",
            "overtime_hours", "method", "can_check_in", "can_check_out", "check_in_time"
        ]

    def get_can_check_out(self, obj):
        return obj.should_show_check_out()

    def get_can_check_in(self, obj):
        return obj.should_show_check_in()

    def get_overtime_hours(self, obj):
        obj.calculate_overtime()
        return obj.overtime_hours

    def get_check_in_time(self, obj):
        return obj.check_in.strftime("%H:%M:%S") if obj.check_in else None