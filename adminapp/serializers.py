from rest_framework import serializers
from teachers.models import *
from students.models import *


class OrderListSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    course_name = serializers.ReadOnlyField(source='course.course_name')
    author = serializers.ReadOnlyField(source='course.author.username')

    class Meta:
        model = Orders
        fields = ['username','author', 'course_name', 'price', 'date_purchased']