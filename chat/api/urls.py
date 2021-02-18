from django.urls import path, re_path

from .views import (
    CreateChatroom,
    ChatList,
    MessagesList,
    CheckRoom,
    UnReadMessageCount
)

app_name = 'chat'

urlpatterns = [
    path('create-room/', CreateChatroom.as_view(), name='create-room'),
    path('chat-list/', ChatList.as_view(), name='chat-list'),
    path('messages/', MessagesList.as_view(), name='messages'),
    path('check-room/', CheckRoom.as_view(), name='check-room'),
    path('unread-message-count/', UnReadMessageCount.as_view(), name='unread-message-count')
]
