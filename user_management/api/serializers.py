from rest_framework import serializers
from  user_management.models import User,TeacherDetails,TeacherDocument
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"password": "Password is required."})
        



class OtpVerificationSerializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)






########################## teacher serializer #######################


class TeacherRegisterSerializer(UserRegisterSerializer):
    class Meta(UserRegisterSerializer.Meta):
        fields = UserRegisterSerializer.Meta.fields

    def create(self, validated_data):
        user_instance = super().create(validated_data)
        user_instance.is_staff = True
        user_instance.save()
        return user_instance


class TeacherDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=TeacherDetails
        fields='__all__'

class TeacherDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model=TeacherDocument
        fields='__all__'