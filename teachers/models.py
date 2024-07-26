from django.db import models
from user_management.models import User
# Create your models here.
class Course(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User')
    course_name=models.CharField(max_length=250)
    description=models.TextField()
    level=models.CharField(max_length=250)
    date_added=models.DateField(auto_now_add=True)
    #demo and thumbnail
    demo_video=models.FileField(upload_to='videos/demo_video',null=True,blank=True)
    thumbnail=models.FileField(upload_to='videos/thumbnails',null=True,blank=True)
    # benefits
    benefit1=models.CharField(max_length=250,blank=True,null=True)
    benefit2=models.CharField(max_length=250,blank=True,null=True)
    benefit3=models.CharField(max_length=250,blank=True,null=True)

    # price section
    original_price=models.CharField(max_length=250)
    offer_price=models.CharField(max_length=250)

    # status of course
    is_accepted=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    is_rejected=models.BooleanField(default=False)
    reject_reason=models.TextField(null=True,blank=True)

    def __str__(self) -> str:
        return f" {self.course_name} added by {self.author.username}"
    
class Videos(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="Course")
    video_name=models.CharField(max_length=250)
    description=models.TextField()
    video=models.FileField(upload_to='video/videos',blank=True,null=True)
    is_accepted=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    is_rejected=models.BooleanField(default=False)
    rejected_reason=models.TextField(null=True,blank=True)
    duration=models.CharField(blank=True, null=True)

    def __str__(self) -> str:
        return f" {self.video_name} of {self.course.course_name}  added by {self.course.author.username}"


