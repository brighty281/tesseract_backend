from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from user_management.api.serializers import *
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework import status
from teachers.serializers import *
from rest_framework import generics
from chats.models import *
from django.db.models import Q
from django.shortcuts import get_object_or_404
class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        user_serializer = UserSerializer(user)

        try:
            user_profile = UserProfile.objects.get(user=user)
            user_profile_serializer = UserProfileSerializer(user_profile)
            data = {
                "user": user_serializer.data,
                "user_profile": user_profile_serializer.data
            }
            return Response(data)
        except UserProfile.DoesNotExist:
            data = {
                "user": user_serializer.data,
                "user_profile": None
            }
            return Response(data)


class UserDetailsUpdate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):

        print('post')
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        print(user_profile)
        serializer = UserProfileUpdateSerializer(user_profile, data=request.data, partial=True)
        print(serializer)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(course_name__icontains=search_query)
            print(queryset)
        return queryset
    

class CheckCoursePurchaseAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, course_id, format=None):
        print(request.user)
        if not request.user:
            return Response({"message": "Authentication credentials were not provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        order = Orders.objects.filter(user=request.user, course_id=course_id).first()  
        serializers=OrderSerializer(order)  
        
        if order:
            return Response({"purchased": True, 'order_id': order.id ,'order':serializers.data}, status=status.HTTP_200_OK)
        else:
            return Response({"purchased": False}, status=status.HTTP_200_OK)



class PurchasedCoursesListAPIView(generics.ListAPIView):
    serializer_class = OrderMycourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        order=Orders.objects.filter(user=user)
        return order

    
class VideoDetailsView(APIView):
    serializers_class=VideoSerializer
    permission_classes=[IsAuthenticated]
    def get(self,request,id,vid):
        try:
            video=Videos.objects.get(course_id=id,id=vid)
            serializer=self.serializers_class(video)
            return Response(serializer.data,status.HTTP_200_OK)
        except Videos.DoesNotExist:
            return Response({"message": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseDetailsView(APIView):
    serializer_class=CourseSerializer
    video_serializer_class=VideoSerializer
    def get(self,request,id):
        try:
            course=Course.objects.get(id=id)
            print(course.id)
            videos=Videos.objects.filter(course_id=course.id)
            print("videos print statemnts")
            print(videos)
            course_serializer=self.serializer_class(course)
            video_serializer=self.video_serializer_class(videos,many=True)
            data={
                'course':course_serializer.data,
                'videos':video_serializer.data
            }
            return Response(data,status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"message":"course not found"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CommentCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        video_id = self.kwargs['video_id']
        comments=Comment.objects.filter(video=video_id).order_by('-id')
        # print(comments)
        return comments 

class ReplyComment(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,comment_id):
        request.data['user']=request.user.id
        print(request.data)
        serializer=ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class GetRepliesView(APIView):
    serializer_class=ReplySerializer
    permission_classes=[IsAuthenticated]
    def get(self,request,comment_id):
        print("reached here")
        print(comment_id)
        comment=Comment.objects.get(id=comment_id)
        replies=Reply.objects.filter(comment=comment)
        serializer=self.serializer_class(replies,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class PreviousChatsView(APIView):
    serializer_class=PreviousChatSerializer
    permission_classes=[IsAuthenticated]
    def get(self,request,student_id,course_id):
        print("student is..",student_id)
        print("course id..",course_id)
        my_messages=ChatMessage.objects.filter(Q(student=student_id,course=course_id))
        serializers=self.serializer_class(my_messages,many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)



class PreviousCommunityChatView(APIView):
    serializers_class=PreviousCommunityChatSerializer
    def get(self,request,community):
        print("community name...",community)
        my_messages=CommunityChatMessages.objects.filter(community=community)
        serializer=self.serializers_class(my_messages,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

# class CourseCommunityListView(APIView):
#      serializer_class=CommunityCourseListSerializer
#      def get(self,request):
#         user = self.request.user
#         commmunities=Orders.objects.filter(user=user)
#         serializer=self.serializer_class(commmunities,many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)
     

class GetTeacherDetailsView(APIView):
    serializer_class=TeacherDetailsSerializer
    def get(self,request,teacher_id):
        print("reacheddd")
        teacherinfo=TeacherDetails.objects.get(user=teacher_id)
        serializer=self.serializer_class(teacherinfo)
        print(serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)
        

    
from rest_framework.decorators import api_view
import razorpay
from django.conf import settings


@api_view(['POST'])
def start_payment(request):
    price = request.data['amount']
    course_id = request.data['course']
    user_id= request.data['user_id']
    print(f"Received price: {price}, course_id: {course_id}, user_id: {user_id}")

    try:
        course = Course.objects.get(pk=course_id)
        user = User.objects.get(pk=user_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    payment = client.order.create({"amount": int(price) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})

    order = Orders.objects.create(user=user,course=course, 
                                 price=price
                               )
    serializer = OrderSerializer(order)
    data = {
        "payment": payment,
        "order": serializer.data
    }

    return Response(data)

