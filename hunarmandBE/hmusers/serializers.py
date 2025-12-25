from rest_framework import serializers
from hmusers.models import Users
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from hmusers.utils import Util
from api.utils import count_jobs

class UserRegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        model = Users
        fields = ['email', 'name', 'password', 'password2', 'phone', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match"
            )
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')

        user = Users.objects.create_user(**validated_data)
        user.role = role
        user.save()

        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255, required=True)
  longitude = serializers.CharField(max_length=50, required=True)
  latitude = serializers.CharField(max_length=50, required=True)
  class Meta:
    model = Users
    fields = ['email', 'password','longitude','latitude']


class UserProfileSerializer(serializers.ModelSerializer):
    
    started_jobs = serializers.SerializerMethodField()
    waiting_jobs = serializers.SerializerMethodField()
    ended_jobs = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    approved_bids = serializers.SerializerMethodField()
    rejected_bids = serializers.SerializerMethodField()

    class Meta:
      model = Users
      fields = ['id','email','name','phone','role','longitude','latitude','started_jobs','waiting_jobs','ended_jobs','total_bids','approved_bids','rejected_bids']
    
    def get_started_jobs(self, obj):
        count = count_jobs(obj.id)
        return count[0]

    def get_waiting_jobs(self, obj):
        count = count_jobs(obj.id)
        return count[1]
    
    def get_ended_jobs(self, obj):
        count = count_jobs(obj.id)
        return count[2]

    def get_total_bids(self, obj):
        count = count_jobs(obj.id)
        return count[3]

    def get_approved_bids(self, obj):
        count = count_jobs(obj.id)
        return count[4]

    def get_rejected_bids(self, obj):
        count = count_jobs(obj.id)
        return count[5]

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, attrs):
    email = attrs.get('email')
    if Users.objects.filter(email=email).exists():
      user = Users.objects.get(email = email)
      uid = urlsafe_base64_encode(force_bytes(user.id))
      #print('Encoded UID', uid)
      token = PasswordResetTokenGenerator().make_token(user)
      #print('Password Reset Token', token)
      link = 'http://localhost:8000/api/user/password/reset-email/'+uid+'/'+token
     # print('Password Reset Link', link)
      # Send EMail
      body = 'Click Following Link to Reset Your Password '+link
      data = {
        'subject':'Reset Your Password',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)
      return attrs
    else:
      raise serializers.ValidationError('You are not a Registered User')
    

class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      password2 = attrs.get('password2')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != password2:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = Users.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')