from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,ListAPIView
from rest_framework.decorators import permission_classes
from user_management.models import *
from .permissions import *
from rest_framework.generics import RetrieveAPIView,ListAPIView

from user_management.api.serializers import *
from students.api.serializers import *
from teachers.serializers import *

from .serializers import *
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from user_management.api.email import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, FloatField, Value
from django.db.models.functions import TruncMonth, TruncYear, Cast
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils import timezone

# Create your views here.

class AdminUserListCreateView(ListCreateAPIView):
    permission_classes=[IsAdmin]
    queryset = User.objects.all().order_by('-date_joined') 
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]

class AcceptUserView(APIView):
    permission_classes = [IsAdmin]
    def patch(self, request, pk, *args, **kwargs):
        print(pk)
        user = get_object_or_404(User, pk=pk)
        
        if 'is_email_verified' in request.data:
            user.is_email_verified = True
            UserProfile.objects.get_or_create(user=user)
            send_approval(user.email)

        elif 'is_active' in request.data:
            user.is_active = request.data['is_active']
            print("block/unblockdone")

        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminTeacherDetailedview(RetrieveAPIView):
      permission_classes = [IsAdmin]
      queryset = User.objects.all()
      serializer_class = UserSerializer
      def retrieve(self, request, *args, **kwargs):
          user_instance = self.get_object()
          teacher_details_instance=TeacherDetails.objects.get(user=user_instance)
          teacher_documents_instance=TeacherDocument.objects.get(user=user_instance)
          teacher_profile_instance=UserProfile.objects.get(user=user_instance)

          user_serializer=self.get_serializer(user_instance)
          teacher_details_serializer=TeacherDetailsSerializer(teacher_details_instance)
          teacher_profile_serializer=UserProfileSerializer(teacher_profile_instance)
          teacher_documents_serializer = TeacherDocumentSerializer(teacher_documents_instance)
          data={   
              'user': user_serializer.data,
              'teacher_details': teacher_details_serializer.data,
              'teacher_documents':teacher_documents_serializer.data,
              'teacher_profile':teacher_profile_serializer.data
          }

          return Response(data, status=status.HTTP_200_OK)


class TeacherDocumentStatusChangeView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    def patch(self, request, id, *args, **kwargs):
        print(id)
        document = get_object_or_404(TeacherDocument, id=id)
        if 'id_verify' in request.data:
            document.id_verify = True
        if 'photo_verify' in request.data:
            document.photo_verify = True
        if 'tenth_verify' in request.data:
            document.tenth_verify = True
        if 'plustwo_verify' in request.data:
            document.plustwo_verify = True
        if 'graduation_verify' in request.data:
            document.graduation_verify = True
        if 'experience_verify' in request.data:
            document.experience_verify = True
       
        
        document.save()

        serializer = TeacherDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllOrdersView(ListAPIView):
    permission_classes=[IsAdmin]
    queryset=Orders.objects.all()
    serializer_class=OrderSerializer

class AllCoursesView(ListAPIView):
    permission_classes=[IsAdmin]
    queryset=Course.objects.all().order_by('-date_added')
    serializer_class=CourseSerializer

class CourseBlockUnblockView(APIView):
    permission_classes=[IsAdmin]
    def patch(self,request,id,*args,**kwargs):
        course = get_object_or_404(Course, id=id)
        print("in the patch")
        if 'is_blocked' in request.data:
            course.is_blocked = request.data['is_blocked']

        course.save()

        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDashboardCards(APIView):
    permission_classes = [IsAdmin]
    def get(self,request):
        user_count=User.objects.filter(is_staff=False,is_superuser=False).count()
        teacher_count=User.objects.filter(is_staff=True,is_superuser=False).count()
        course_count=Course.objects.all().count()
        orders=Orders.objects.all().count()
        blocked_users=User.objects.filter(is_staff=False,is_superuser=False,is_active=False).count()
        blocked_teachers=User.objects.filter(is_staff=True,is_active=False).count()
        blocked_courses=Course.objects.filter(is_accepted=True,is_blocked=True).count()
        videos=Videos.objects.filter().count()
        data={
            'user':user_count,
            'teacher':teacher_count,
            'course':course_count,
            'orders':orders,
            'videos':videos,

            'buser':blocked_users,
            'bteacher':blocked_teachers,
            'bcourse':blocked_courses
        }
        print(data)
        return Response(data,status=status.HTTP_200_OK)


class AdminDashboardOrderList(ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = Orders.objects.all().order_by('-date_purchased')  
    serializer_class = OrderListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['course_name']


class OrdersGraphView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        six_months_ago = now() - timedelta(days=30*6)
        orders = Orders.objects.filter(date_purchased__gte=six_months_ago)

        monthly_orders = orders.annotate(
            year_month=TruncMonth('date_purchased')
        ).values('year_month').annotate(
            total_orders=Count('id')
        ).order_by('year_month')

        # Convert queryset to dictionary
        orders_data = [
            {
                'year_month': order['year_month'].strftime('%Y-%m'),
                'total_orders': order['total_orders']
            }
            for order in monthly_orders
        ]
 

        return JsonResponse(orders_data, safe=False)

class OrderGraphYearView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        yearly_data = Orders.objects.annotate(
            year=TruncYear('date_purchased')
        ).values('year').annotate(
            total_orders=Count('id')
        ).order_by('year')

        formatted_yearly_data = [{'year_month': item['year'].strftime('%Y'), 'total_orders': item['total_orders']} for item in yearly_data]

        return JsonResponse(formatted_yearly_data, safe=False)
    
class OrdersByWeekView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, *args, **kwargs):
        today = datetime.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=1, month=today.month+1) - timedelta(days=1)

        orders = Orders.objects.filter(date_purchased__range=[first_day_of_month, last_day_of_month])

        num_weeks = (last_day_of_month - first_day_of_month).days // 7 + 1

        orders_by_week = {}
        for week_number in range(num_weeks):
            start_of_week = first_day_of_month + timedelta(weeks=week_number)
            end_of_week = min(start_of_week + timedelta(days=6), last_day_of_month)
            week_name = f"Week {week_number + 1}"
            orders_in_week = orders.filter(date_purchased__range=[start_of_week, end_of_week])
            orders_by_week[week_name] = orders_in_week.count()

        return JsonResponse(orders_by_week)

class TodaysSalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        today = timezone.now().date()
        orders_today = Orders.objects.filter(date_purchased=today)
        orders_today_count = Orders.objects.filter(date_purchased=today).count()
        order_list = Orders.objects.filter(date_purchased=today).order_by('-date_purchased') 
        serializer = OrderListSerializer(order_list, many=True)

        total_courses_ordered = orders_today.values('course').distinct().count()

        unique_user_ids = set(order.user.id for order in order_list)
        unique_users_count = len(unique_user_ids)

        total_earnings = sum(int(order.price) for order in orders_today if int(order.price))

        data = {
            'orders_today_count': orders_today_count,
            'users_count': unique_users_count,
            'course_count':total_courses_ordered,
            'order_list': serializer.data,
            'total_earnings': total_earnings,
        }
        return Response(data, status=status.HTTP_200_OK)

class MonthlySalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=1, month=today.month+1) - timedelta(days=1)

        orders_this_month = Orders.objects.filter(date_purchased__range=(first_day_of_month, last_day_of_month))


        orders_this_month_count = orders_this_month.count()
        total_courses_ordered = orders_this_month.values('course').distinct().count()

        unique_user_ids = set(order.user.id for order in orders_this_month)
        unique_users_count = len(unique_user_ids)

        total_earnings = sum(int(order.price) for order in orders_this_month if order.price.isdigit())

        serializer = OrderListSerializer(orders_this_month.order_by('-date_purchased'), many=True)

      
        data = {
            'orders_this_month_count': orders_this_month_count,
            'users_count': unique_users_count,
            'course_count': total_courses_ordered,
            'order_list': serializer.data,
            'total_earnings': total_earnings,
        }
        return Response(data, status=status.HTTP_200_OK)
    

class YearlySalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        today = timezone.now().date()
        first_day_of_year = today.replace(month=1, day=1)
        last_day_of_year = today.replace(month=12, day=31)


        orders_this_year = Orders.objects.filter(date_purchased__range=(first_day_of_year, last_day_of_year))

        orders_this_year_count = orders_this_year.count()
        total_courses_ordered = orders_this_year.values('course').distinct().count()

        unique_user_ids = set(order.user.id for order in orders_this_year)
        unique_users_count = len(unique_user_ids)

        total_earnings = sum(int(order.price) for order in orders_this_year if order.price.isdigit())


        serializer = OrderListSerializer(orders_this_year.order_by('-date_purchased'), many=True)

        data = {
            'orders_this_year_count': orders_this_year_count,
            'users_count': unique_users_count,
            'course_count': total_courses_ordered,
            'order_list': serializer.data,
            'total_earnings': total_earnings,
        }
        return Response(data, status=status.HTTP_200_OK)
    

class WeeklySalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        orders_this_week = Orders.objects.filter(date_purchased__range=(start_of_week, end_of_week))

        orders_this_week_count = orders_this_week.count()
        total_courses_ordered = orders_this_week.values('course').distinct().count()

        unique_user_ids = set(order.user.id for order in orders_this_week)
        unique_users_count = len(unique_user_ids)

        total_earnings = sum(int(order.price) for order in orders_this_week if order.price.isdigit())

        serializer = OrderListSerializer(orders_this_week.order_by('-date_purchased'), many=True)

        data = {
            'orders_this_week_count': orders_this_week_count,
            'users_count': unique_users_count,
            'course_count': total_courses_ordered,
            'order_list': serializer.data,
            'total_earnings': total_earnings,
        }
        return Response(data, status=status.HTTP_200_OK)

