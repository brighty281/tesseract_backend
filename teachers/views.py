from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from . serializers import CourseSerializer,VideoSerializer,OrderSerializer,ChatTeacherSerializer
from students.api.serializers import *
from user_management.api.serializers import UserSerializer
from adminapp.serializers import OrderListSerializer
from students.models import *
from rest_framework import generics
from rest_framework.generics import RetrieveAPIView,ListAPIView
from . models import Course,Videos
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
import os
from datetime import datetime, timedelta
import cv2
from django.db.models import Q
from django.db.models import Count, Sum, FloatField, Value
from django.db.models.functions import TruncMonth, TruncYear, Cast
# Create your views here.
class AddCourseView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        # mutable_data = request.data.copy()
        # mutable_data['added_by'] = request.user.id
        data = request.data.dict()
        data['author'] = request.user.id
        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# video

class MyCoursesListview(generics.ListAPIView):
    serializer_class=CourseSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_authenticated:
            c=Course.objects.filter(author_id=user.id)
            print(c)
            return Course.objects.filter(author_id=user.id)
        else:
            print('s')
            return Course.objects.none() 

# class CourseDetailView(generics.RetrieveAPIView):
#     serializer_class = CourseSerializer
#     lookup_url_kwarg = 'id'

#     def get_queryset(self):
#         queryset = Course.objects.filter(id=self.kwargs.get(self.lookup_url_kwarg))
#         return queryset

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)

class CourseDetailView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        course_instance = self.get_object()
        video_instances = Videos.objects.filter(course=course_instance)

        course_serializer = self.get_serializer(course_instance)
        video_serializer = VideoSerializer(video_instances, many=True)

       

        data = {
            'course': course_serializer.data,
            'videos': video_serializer.data
        }
        
        return Response(data, status=status.HTTP_200_OK)


class CourseStatusChangeView(APIView):
    def patch(self, request, id, *args, **kwargs):
        course = get_object_or_404(Course, id=id)
        print(course)
        if 'is_blocked' in request.data:
            course.is_blocked = request.data['is_blocked']

        course.save()

        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)




class AddCourseVideo(APIView):
    def post(self,request,*args, **kwargs):
        try:
            video_file = request.data['video']
            with open('temp_video.mp4', 'wb') as temp_file:
                for chunk in video_file.chunks():
                    temp_file.write(chunk)

            # Read the video file and extract duration
            video_capture = cv2.VideoCapture('temp_video.mp4')
            frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            duration_seconds = round(frames / fps)
            video_duration = timedelta(seconds=duration_seconds)  # Use timedelta from datetime module
            print(video_duration)
            video_capture.release()

            # Delete the temporary video file
            os.remove('temp_video.mp4')

            serializer = VideoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(duration=video_duration)
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TeacherOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    def get(self,request):
        author=self.request.user
        orders=Orders.objects.filter(course__author=author)
        serializer=self.serializer_class(orders,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# filter the students of a particular teacher based on the orders
class TeacherChatView(generics.ListAPIView):
    serializer_class=UserSerializer
    def get(self,request):
        author=self.request.user
        orders=Orders.objects.filter(course__author=author)
        students=User.objects.filter(Q(orders__in=orders)).distinct()
        serializer=self.serializer_class(students,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class TeacherDashboardData(APIView):
    def get(self,request):
        teacher=request.user.id
        orders=Orders.objects.filter(course__author=teacher)
        total_orders=orders.count()

        total_students=orders.values('user').distinct().count()

        courses=Course.objects.filter(author=teacher)
        total_course=courses.count()
        total_videos = Videos.objects.filter(course__in=courses).count()

        total_amount = orders.annotate(price_float=Cast('price', FloatField())).aggregate(
            total_price=Sum('price_float')
        )['total_price']

        total_blocked_courses=orders.filter(course__is_blocked=True).values('course').distinct().count()

        serializer=OrderListSerializer(orders,many=True)

        data={
            'total_course':total_course,
            'total_order':total_orders,
            'total_students':total_students,
            'total_amount':total_amount,
            'total_blocked_courses':total_blocked_courses,
            'total_videos':total_videos,
            'orders':serializer.data,
            
        }

        # print(data)
        return Response(data,status=status.HTTP_200_OK)




class TeacherOrdersGraphView(APIView):
    def get(self, request):
        six_months_ago = now() - timedelta(days=30*6)
        print('user',request.user)
        
       
        user_courses = Course.objects.filter(author=request.user.id)
        print('user_courses',user_courses)
        orders = Orders.objects.filter(course__in=user_courses, date_purchased__gte=six_months_ago)

        print('orders',orders)

        monthly_orders = orders.annotate(
            year_month=TruncMonth('date_purchased')
        ).values('year_month').annotate(
            total_orders=Count('id')
        ).order_by('year_month')
        
        orders_data = [
            {
                'year_month': order['year_month'].strftime('%Y-%m'),
                'total_orders': order['total_orders']
            }
            for order in monthly_orders
        ]

        print(orders_data)

        return JsonResponse(orders_data, safe=False)