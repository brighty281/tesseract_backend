from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . serializers import *
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed,ParseError
from user_management.models import User,UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .email import *

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(email)
        print(password)
        myuser=User.objects.get(email=email)
        print(myuser)
        user = authenticate(username=email, password=password)  # Use email as username
        print(user)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        elif not user.is_active:
            return Response({'error': 'Blocked'}, status=status.HTTP_403_FORBIDDEN)
        
        else:
            if not user.is_staff:
                UserProfile.objects.get_or_create(user=user)
                refresh = RefreshToken.for_user(user)
                refresh['username'] = str(user.username)

                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                content = {
                    'userid': user.id,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'isAdmin': user.is_superuser,
                }
                return Response(content, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'This account is not a user account'}, status=status.HTTP_401_UNAUTHORIZED)


# class RegisterView(APIView):
#     def post(self,request):
#         serializer=UserRegisterSerializer(data=request.data)
#         print(serializer)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE,)  
#         content ={'Message':'User Registered Successfully'}
#         return Response(content,status=status.HTTP_201_CREATED,)


class RegisterView(APIView):
    def post(self,request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user=serializer.save(is_active=False)
                UserProfile.objects.get_or_create(user=user) 
                send_otp_via_email(user.email,user.otp)
                response_data = {
                    'message': 'OTP sent successfully.',
                    'email': user.email  
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                print(f"Error during user registration: {e}")
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(serializer._errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        print('superuser status',user.is_superuser)
        print('is_teacher status',user.is_staff)
        data = UserSerializer(user).data
        content = data
        return Response(content)
    


class OtpVerification(APIView):
    def post(self,request):
        serializer=OtpVerificationSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            print('valid serializer')
            try:
                email = serializer.validated_data.get('email')
                entered_otp = serializer.validated_data.get('otp')
                
                user = User.objects.get(email=email )
                print(user)

                if user.otp==entered_otp:
                    print('otp_valid')
                    user.is_active=True
                    user.save()
                    return Response({'message': 'User registered and verified successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP,Please Check your email and Verify'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found or already verified'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print(f"Error during OTP verification: {e}")
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ForgotPassword(APIView):
    def post(self,request,*args, **kwargs):
        email=request.data.get('email')
        try:
            user=User.objects.get(email=email)
            send_otp_via_email(user.email,user.otp)
            response_data={
                'message':'OTP sent successfully',
                'email':user.email,
                'user_id':user.id,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'exists': False, 'message': 'Invalid Email.'}, status=status.HTTP_404_NOT_FOUND)



class ChangePassword(APIView):
    def post(self,request,*args,**kwargs):
        user_id=self.kwargs.get('id')
        print(user_id)
        new_password = request.data.get('password')
        print("#######")
        print(new_password)
        try:
            user=User.objects.get(id=user_id)
            user_password=make_password(new_password)
            user.password=user_password
            user.save()

            return Response({'success':True,'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)





###################   teacher's section ########################################################

class TeacherRegisterView(APIView):
    def post(self,request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({'email': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer=TeacherRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user=serializer.save(is_active=False)
                UserProfile.objects.get_or_create(user=user) 
                send_otp_via_email(user.email,user.otp)
                response_data = {
                    'message': 'OTP sent successfully.',
                    'email': user.email,
                    'user_id':user.id
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            except Exception as e:
                print(f"Error during user registration: {e}")
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(serializer._errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherDetails(APIView):
    def post(self,request):
        user_id=request.data.get('user')
        if user_id:
            try:
                user=User.objects.get(id=user_id)
                print(user)
                serializer=TeacherDetailsSerializer(data=request.data)
                if serializer.is_valid():
                    teacher_details=serializer.save(user=user)
                    response_data={
                        'message':'teacher_details saved successfully'
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
        
            return Response({'error': 'email not provided.'}, status=status.HTTP_400_BAD_REQUEST)

class TeacherDocuments(APIView):
    def post(self,request):
        print("hello")
        user_id=request.data.get('user')
        print(user_id)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(user)
                serializer = TeacherDocumentSerializer(data=request.data)
                print(serializer.is_valid())
                if serializer.is_valid():
                    serializer.save(user=user)
                    response_data = {
                        'message': 'Teacher documents saved successfully.'
                    }
                    print(response_data)
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'User ID not provided.'}, status=status.HTTP_400_BAD_REQUEST)



class TeacherLoginView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password) 
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        elif not user.is_active:
            return Response({'error': 'Blocked'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if not user.is_superuser and user.is_staff and user.is_active:
                refresh = RefreshToken.for_user(user)
                refresh['username'] = str(user.username)

                access_token = refresh.access_token
                refresh_token = str(refresh)

                content = {
                    'access_token': str(access_token),
                    'refresh_token': refresh_token,
                    'userid':user.id,
                    'isAdmin': user.is_superuser,
                    'isTeacher': user.is_staff,
                    'isEmailverified':user.is_email_verified
                }
                return Response(content, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials or user is not a teacher'}, status=status.HTTP_401_UNAUTHORIZED)




class AdminLoginView(APIView):
    def post(self,request):
        email=request.data['email']
        password=request.data['password']

        user=authenticate(username=email,password=password)

        if user.is_superuser:
            refresh = RefreshToken.for_user(user)
            refresh['username'] = str(user.username)

            access_token = refresh.access_token
            refresh_token = str(refresh)

            content = {
                'access_token': str(access_token),
                'refresh_token': refresh_token,
                'isAdmin': user.is_superuser,
            }
        elif user.is_staff:
            return Response({'This account is not a Superuser account'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(content, status=status.HTTP_200_OK)
