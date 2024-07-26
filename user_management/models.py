from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_user(self,username,email,password=None):
        if not email:
            raise ValueError('User Must Have An Email Adress')
            
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self,username,email,password):
        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,
                                )
        user.is_active = True
        user.is_superuser = True
        user.is_email_verified = True
        user.is_staff = True
        
        user.save(using=self._db)
        return user
            

class User(AbstractBaseUser):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100,unique=True)
    
    
    #required field
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.username
    
    def has_perm(self,perm,obj=None):
        return self.is_superuser
    
    def has_module_perms(self,add_label):
        return True

class UserProfile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="User_Profile")
    profile_pic=models.ImageField(upload_to='profile_pic',blank=True,null=True)
    phone=models.CharField(max_length=250,blank=True,null=True)
    social_link1=models.CharField(max_length=250,blank=True,null=True)
    social_link2=models.CharField(max_length=250,blank=True,null=True)
    about=models.TextField(blank=True,null=True)
    current_role=models.CharField(max_length=250,blank=True,null=True)
    def __str__(self):
        return f"profile of {self.user.username}" 
    def save(self, *args, **kwargs):
        if not self.profile_pic:
            self.profile_pic = '/profile_pic/default/userprofile.webp'
        super().save(*args, **kwargs)


class TeacherDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    experience = models.PositiveIntegerField()
    address = models.TextField()
    def __str__(self):
        return self.user.username if self.user else 'TeacherDetails'

class TeacherDocument(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    id_proof = models.FileField(upload_to='teacher_documents/id_proof')
    id_verify=models.BooleanField(default=False)
    id_block=models.BooleanField(default=False)

    photo_proof = models.FileField(upload_to='teacher_documents/photo')
    photo_verify=models.BooleanField(default=False)
    photo_block=models.BooleanField(default=False)

    tenth_proof = models.FileField(upload_to='teacher_documents/tenth_proof')
    tenth_verify=models.BooleanField(default=False)
    tenth_block=models.BooleanField(default=False)

    plustwo_proof = models.FileField(upload_to='teacher_documents/plustwo_proof')
    plustwo_verify=models.BooleanField(default=False)
    plustwo_block=models.BooleanField(default=False)

    experience_proof = models.FileField(upload_to='teacher_documents/experience_proof')
    experience_verify=models.BooleanField(default=False)
    experience_block=models.BooleanField(default=False)

    graduation_proof = models.FileField(upload_to='teacher_documents/graduation_proof')
    graduation_verify=models.BooleanField(default=False)
    graduation_block=models.BooleanField(default=False)
    
    is_document_verified=models.BooleanField(default=False)

    def __str__(self):
            return self.user.username if self.user else 'Document'


