from rest_framework import serializers
from user_management.models import *
from students.models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [ 'profile_pic', 'phone', 'social_link1', 'social_link2', 'about']


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(many=False, read_only=True)  
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login', 'is_superuser', 'is_email_verified', 'is_staff', 'is_active', 'otp', 'user_profile']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)  

    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'phone', 'social_link1', 'social_link2', 'about', 'username']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    is_teacher=serializers.ReadOnlyField(source='user.is_staff')
    user_profile = serializers.SerializerMethodField() 

    class Meta:
        model = Comment
        fields = ['id', 'user','username','is_teacher', 'user_profile', 'course', 'video', 'comment', 'date_added']

    def get_user_profile(self, obj):
        user_profile = obj.user.User_Profile.first() 
        return UserProfileSerializer(user_profile).data if user_profile else None 

class ReplySerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_profile = serializers.SerializerMethodField() 
    is_teacher=serializers.ReadOnlyField(source='user.is_staff')
    class Meta:
        model = Reply
        fields = ['id', 'comment','username','is_teacher','user_profile', 'user', 'reply_text', 'date_added']

    def get_user_profile(self, obj):
        user_profile = obj.user.User_Profile.first() 
        return UserProfileSerializer(user_profile).data if user_profile else None 