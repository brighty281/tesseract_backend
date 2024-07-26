from django.urls import path
from . views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns =  [
    path('token/', TokenObtainPairView.as_view(serializer_class=MyTokenObtainPairSerializer), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/',LoginView.as_view(),name="user-login"),
    path('signup/',RegisterView.as_view(),name="register-view"),
    path('userdetails/',UserDetails.as_view(),name="user-details"),
    path('otpverify/',OtpVerification.as_view(),name='otp_verify'),
    path('fpassword/',ForgotPassword.as_view(),name="fpassword"),
    path('changepassword/<int:id>/',ChangePassword.as_view(),name="change_password"),

    
    path('teacher/signup/',TeacherRegisterView.as_view(),name="teacher-register"),
    path('teacher/login/',TeacherLoginView.as_view(),name="teacher-login"),
    path('teacher/teacher_details/',TeacherDetails.as_view(),name="teacher-details"),
    path('teacher/teacher_documents',TeacherDocuments.as_view(),name='teacher-documents'),
    path('admin/admin_login/',AdminLoginView.as_view(),name="admin-login")
]