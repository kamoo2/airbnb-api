import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer
from rooms.serializers import RoomSerializer
from .models import User
from rooms.models import Room


# create account : POST -> api/v1/users
class UsersView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(UserSerializer(new_user).data)
        else:
            return Response(data=serializers.errors, status=status.HTTP_400_BAD_REQUEST)


# Login View는 별기능이 없으니 FBV로 만들자
@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    # 장고는 authentication function이 있다.
    # 이 function은 username과 password를 비교해 맞으면 그 user를 return 해준다.

    user = authenticate(username=username, password=password)
    # 우리는 일치하는 인증된 user를 얻었다.
    # 이 user를 JWT(JSON WEB TOKEN)으로 보내줘야함
    if user is not None:
        encoded_jwt = jwt.encode(
            {"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256"
        )
        return Response(data={"token": encoded_jwt})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # jwt에는 절때 네버 민감한정보는 담아서는 안된다.
    # 근데 의문점은 이 토큰을 jwt.io에서 너무쉽게 decoded해 안의 정보를 볼수 있다.
    # 그럼 왜쓰냐 이건데
    # 우리의 server는 token이 다른사람에의해 수정되었냐를 체크할수있다.
    # jwt를 쓰는이유는 그 누구도 우리의 token을 건들지 않았다는 것을 확인하는 용도이다.
    # 다시말하면 데이터(token안의 정보)를 아무도 못보게 암호화하는 것이 목적이아니라
    # 이 데이터를 누군가가 건드렸느냐 아니면 그대로이냐가 더 중요한 Point임
    # 프론트엔드에서 이 토큰을 받아서 header로 전송해주면 그 token은 decode 과정을 거쳐
    # 실제정보로 변환된다.


class MyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RoomSerializer(user.favs.all(), many=True).data
        return Response(serializer)

    def put(self, request):
        pk = request.data.get("pk", None)
        user = request.user
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                if room in user.favs.all():
                    user.favs.remove(room)
                else:
                    user.favs.add(room)
                serializer = RoomSerializer(user.favs.all(), many=True).data
                return Response(serializer)
            except Room.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# GET : api/v1/users/12
@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user).data
        return Response(serializer)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
