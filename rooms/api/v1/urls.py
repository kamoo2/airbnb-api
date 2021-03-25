from django.urls import path, include
from ... import views

app_name = "rooms"


urlpatterns = [
    # path("", views.ListRoomView.as_view()),
    # path("<int:pk>/", views.SeeRoomView.as_view()),
    path("", views.RoomsView.as_view()),
    path("<int:pk>/", views.RoomView.as_view()),
    path("search/", views.room_search),
]