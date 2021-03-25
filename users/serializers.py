from .models import User
from rest_framework import serializers


class RelatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "superhost",
        )


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "superhost",
            "password",
        )

        read_only_fields = (
            "id",
            "superhost",
            "avatar",
        )

    def create(self, validated_data):
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    # 다음과 같은은 작업은 serializers.Serializer을 상속받았을때만 해주면된다.
    # ModelSerializer는 알아서 다해준다.
    # def update(self, instance, validated_data):
    #     instance.username = validated_data.get("username", instance.username)
    #     instance.first_name = validated_data.get("first_name", instance.first_name)
    #     instance.last_name = validated_data.get("last_name", instance.last_name)
    #     instance.email = validated_data.get("email", instance.email)
    #     instance.avatar = validated_data.get("avatar", instance.avatar)
    #     instance.save()
    #     return instance

    def validate_first_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("글자가 너무 짧습니다.")
        else:
            return value.capitalize()
