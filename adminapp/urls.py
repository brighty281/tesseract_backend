from .views import *
from django.urls import path

urlpatterns=[
    path('users/', AdminUserListCreateView.as_view(), name='users'),
    path('users/status/<int:pk>/', AcceptUserView.as_view(), name='accept_teachers_view'),

    path('teachers/accept/<int:pk>/', AcceptUserView.as_view(), name='accept_teachers_view'),
    path('teachers/teacher_details/<int:pk>/',AdminTeacherDetailedview.as_view(),name='teacher-details'),
    path('teachers/document_verify/<int:id>/',TeacherDocumentStatusChangeView.as_view(),name='teacher-verify'),

    #order
    path('all_orders/',AllOrdersView.as_view(),name='all-orders'),
    path("all_courses/",AllCoursesView.as_view(),name='all_courses'),

    path("course_status/<int:id>/",CourseBlockUnblockView.as_view(),name='courses_status'),


    #dashboard section
    path('admin_cards/',AdminDashboardCards.as_view(),name='dashboard-cards'),
    path('dashboard_orders/',AdminDashboardOrderList.as_view(),name='dashboard-Orders'),
    path('order_graph/', OrdersGraphView.as_view()),
    path('order_graph_year/', OrderGraphYearView.as_view()),
    path('order_graph_week/', OrdersByWeekView.as_view()),

    #sales report
    path('todays_report/',TodaysSalesReportView.as_view()),
    path('monthly_report/',MonthlySalesReportView.as_view()),
    path('weekly_report/',WeeklySalesReportView.as_view()),
    path('yearly_report/',YearlySalesReportView.as_view()),
    
]