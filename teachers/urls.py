from .views import *
from django.urls import path

urlpatterns=[
    path("add_course/",AddCourseView.as_view(),name='add_course'),
    path("my_courses/",MyCoursesListview.as_view(),name='my_courses'),
    path('course_view/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('course_status/<int:id>/', CourseStatusChangeView.as_view(), name='course_status'),
    path('add_video/',AddCourseVideo.as_view(),name='add_video'),

    #teacher order
    path('teacherorders_view/',TeacherOrdersView.as_view(),name='order_view'),
    path('teacher_chat/',TeacherChatView.as_view(),name='chat_teacher'),

    #teacher dashboard section
    path('teacherdashboard_orderdata/',TeacherDashboardData.as_view(),name='teacher-dashboard'),
    path('teacherdashboard_graphview/',TeacherOrdersGraphView.as_view(),name='teacher-graph'),
]