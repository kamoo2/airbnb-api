from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .serializers import RoomSerializer
from .models import Room


# I want to see All Rooms

# USE 1. api_view decorators

# @api_view(["GET"])
# def list_rooms(request):
#     rooms = Room.objects.all()
#     serializer = RoomSerializer(rooms, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# USE 2. APIView

# class ListRoomView(APIView):
#     def get(self, request):
#         rooms = Room.objects.all()
#         serializer = RoomSerializer(rooms, many=True)
#         return Response(serializer.data)

# USE 3. ListAPIView


# class ListRoomView(ListAPIView):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer

# def get_queryset(self):
#     qureyset = self.queryset
#     qureyset = qureyset.filter(bedrooms__gt=2).filter(user__superhost=True)
#     return qureyset


# I Want to See One Room

# 1 . Use RetrieveAPIView


# class SeeRoomView(RetrieveAPIView):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer


# @api_view(["GET", "POST"])
# def rooms_view(request):
#     if request.method == "GET":
#         rooms = Room.objects.all()[:5]
#         serializer = RoomSerializer(rooms, many=True).data
#         return Response(serializer)
#     elif request.method == "POST":
#         if not request.user.is_authenticated:
#             r eturn Response(status=status.HTTP_401_UNAUTHORIZED)
#         serializer = RoomSerializer(data=request.data)
#         if serializer.is_valid():
#             room = serializer.save(user=request.user)
#             room_serializer = RoomSerializer(room).data
#             return Response(room_serializer, status=status.HTTP_201_CREATED)
#         else:
#             return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnPagination(PageNumberPagination):
    page_size = 20


class RoomsView(APIView):
    def get(self, request):
        paginator = OwnPagination()
        rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        serializer = RoomSerializer(results, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomView(APIView):
    def get_room(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        # room = get_object_or_404(Room, pk=pk)
        room = self.get_room(pk)
        if room is not None:
            serializer = RoomSerializer(room).data
            return Response(serializer)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = RoomSerializer(room, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room(pk)
        if room.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if room is not None:
            room.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# search view를 만들어볼껀데 매우 구체적이기 때문에 FBV 사용하는 것이 좋음


@api_view(["GET"])
def room_search(request):
    # 아래 두줄을 paginator = OwnPagination() 으로 줄여줄수 있지만
    # Custom pagination 사용하지 않을때도 알아야하니깐 나두자
    max_price = request.GET.get("max_price", None)
    min_price = request.GET.get("min_price", None)
    beds = request.GET.get("beds", None)
    bedrooms = request.GET.get("bedrooms", None)
    bathrooms = request.GET.get("bathrooms", None)
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)

    filter_kwargs = {}
    if max_price is not None:
        filter_kwargs["price__lte"] = max_price
    if min_price is not None:
        filter_kwargs["price__gte"] = min_price
    if beds is not None:
        filter_kwargs["beds__gte"] = beds
    if bedrooms is not None:
        filter_kwargs["beds__gte"] = bedrooms
    if bathrooms is not None:
        filter_kwargs["beds__gte"] = bathrooms
    if lat is not None and lng is not None:
        filter_kwargs["lat__gte"] = float(lat) - 0.005
        filter_kwargs["lat__lte"] = float(lat) + 0.005
        filter_kwargs["lng__gte"] = float(lng) - 0.005
        filter_kwargs["lng__lte"] = float(lng) + 0.005

    paginator = PageNumberPagination()
    paginator.page_size = 10
    try:
        rooms = Room.objects.filter(**filter_kwargs)
    except ValueError:
        rooms = Room.objects.all()
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)

    # generic. 하위 버전의 View에서 pagination 기능 추가하는법
    # 1. PageNumberPagination을 추가하여 paginator 객체 생성
    # 2. paginator의 page_size 설정
    # 3. 본래 serializer에 객체나 쿼리셋 연결해주는 작업 사이에 paginator.paginate_queryset(rooms,request)
    # 여기서 paginate_queryset에 request를 넣어주는 이유는 넣어줌으로써 query param ? 을 사용할수있다.
    # 따라서 search/?page=2 이런식으로 사용가능
    # 또한 Response를 이용해 serializer를 보여주는게 아니라
    # painator.get_paginated_response를 이용해 serializer.data를 보여준다.
    # 이렇게 response 하게 되면 각 페이지마다 이전페이지 이후페이지의 url 정보가 담겨있기때문
