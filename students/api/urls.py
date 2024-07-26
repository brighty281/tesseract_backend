from .views import *
from django.urls import path

urlpatterns =  [
    path("user_details/", UserDetails.as_view(), name="user_details"),
    path("user_details_update/",UserDetailsUpdate.as_view(), name="user-details-update"),
    path("course_list/",CourseListCreateAPIView.as_view(),name="course_list"),

    path("purchased/<int:course_id>/",CheckCoursePurchaseAPIView.as_view(),name="check-purchased"),
    path('enrolled_courses/',PurchasedCoursesListAPIView.as_view(),name='enrolled_courses'),

    path('video_details/<int:id>/<int:vid>/', VideoDetailsView.as_view(),name='video-view'),
    path('course_details/<int:id>/',CourseDetailsView.as_view(),name='course-details'),
    path('add_comment/',CommentCreateView.as_view(),name='add_comment'),
    path('video_comments/<int:video_id>/', VideoCommentsView.as_view(), name='video_comments'),
    path('replycomment/<int:comment_id>/',ReplyComment.as_view(),name='reply-comment'),
    path('getreply/<int:comment_id>/',GetRepliesView.as_view(),name='get-replies'),
    path('getteacher_details/<int:teacher_id>/',GetTeacherDetailsView.as_view(),name='get-teacherdetails'),

    #fetch chat

    path('previous_chats/<int:student_id>/<int:course_id>/',PreviousChatsView.as_view(),name='previous_chat'),
    path('previous_community_chats/<str:community>/',PreviousCommunityChatView.as_view(),name='previous_community_chat'),
    # path('community_courselist/',CourseCommunityListView.as_view(),name='community_courselist'),

    #payment url
    path('pay/', start_payment, name="payment"),
]
