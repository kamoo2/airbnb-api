from rest_framework import serializers
from .models import Room
from users.serializers import RelatedUserSerializer


class ReadRoomSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "price",
            "bedrooms",
            "instant_book",
            "user",
        )


class WriteRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "name",
            "address",
            "price",
            "beds",
            "lat",
            "lng",
            "bedrooms",
            "bathrooms",
            "check_in",
            "check_out",
            "instant_book",
        )

    def validate(self, data):
        if self.instance:  # update인 경우
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)
        else:  # create인 경우
            check_in = data.get("check_in")
            check_out = data.get("check_out")

        if check_in == check_out:
            raise serializers.ValidationError("check_in & check_out은 같아서는 안됩니다.")
        return data


# WriteRoomSerializer + ReadRoomSerializer
class RoomSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    is_fav = serializers.SerializerMethodField()

    class Meta:
        model = Room
        exclude = ("modified",)
        read_only_fields = ("user", "id", "created", "updated")

    def validate(self, data):
        if self.instance:  # update인 경우
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)
        else:  # create인 경우
            check_in = data.get("check_in")
            check_out = data.get("check_out")

        if check_in == check_out:
            raise serializers.ValidationError("check_in & check_out은 같아서는 안됩니다.")
        return data

    def get_is_fav(self, obj):
        request = self.context.get("request")
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.favs.all()
        return False
