from rest_framework import serializers
from .models import Course,Videos
from students.models import Orders
from chats.models import *

class CourseSerializer(serializers.ModelSerializer):
    demo_video = serializers.FileField(required=False)
    thumbnail = serializers.FileField(required=False)
    user = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields= '__all__'

        
    def get_user(self, obj):
        return obj.author.username

class VideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=False)
    class Meta:
        model = Videos
        exclude = ( 'is_blocked',)

class OrderSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='course.author.username')
    username = serializers.ReadOnlyField(source='user.username')
    course_name = serializers.ReadOnlyField(source='course.course_name')
    original_price=serializers.ReadOnlyField(source='course.original_price')

    class Meta:
        model = Orders
        fields = ['user','author', 'course','course_name', 'price', 'date_purchased','username','original_price'] 


class OrderMycourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = Orders
        fields = ['user', 'course', 'price', 'date_purchased'] 

class ChatTeacherSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='user.username')
    course_name = serializers.ReadOnlyField(source='course.course_name')
    class Meta:
        model=Orders
        fields=['user','username','course_name']
    

class PreviousChatSerializer(serializers.ModelSerializer):
    class Meta:
        model=ChatMessage
        fields='__all__'

class PreviousCommunityChatSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='sender.username')
    is_teacher=serializers.ReadOnlyField(source='sender.is_staff')
    class Meta:
        model=CommunityChatMessages
        fields=['username','is_teacher','sender','message','community','timestamp']


# class CommunityCourseListSerializer(serializers.ModelSerializer):
#     course_name=serializers.ReadOnlyField(source='course.course_name')
#     author=serializers.ReadOnlyField(source='course.author')
#     class Meta:
#         model=Orders
#         fields=['course_name','author']