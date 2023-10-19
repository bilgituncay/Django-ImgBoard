from django.urls import path
from direct_messages.views import *

urlpatterns = [
    path('inbox/', ListCoversations.as_view(), name='conversations'),
    path('inbox/create-conversation', CreateConversation.as_view(), name='create-conversation'),
    path('inbox/<int:pk>', ConversationView.as_view(), name='conversation'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name='create-message')
]