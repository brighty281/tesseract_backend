from django.db import models
from user_management.models import User
from teachers.models import Course
# Create your models here.
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name='student', on_delete=models.CASCADE,null=True)
    course=models.ForeignKey(Course,related_name='course',on_delete=models.CASCADE,null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.course}: {self.message[:20]}'


class CommunityChatMessages(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)
    community=models.CharField(max_length=250,null=True)       

    def __str__(self):
        return f'Community of {self.community} message by {self.sender} : {self.message[:20]}'