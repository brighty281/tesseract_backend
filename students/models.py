from django.db import models
from user_management.models import*
from teachers.models import *

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_purchased = models.DateField(auto_now_add=True, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"order by {self.user.username} - course {self.course.course_name}"

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    video=models.ForeignKey(Videos,on_delete=models.CASCADE)
    comment=models.CharField(max_length=255)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return f" comment of '{self.user.username}' -  on - {self.video.video_name} - {self.course.course_name}"

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by '{self.user.username}' - {self.comment.comment}"