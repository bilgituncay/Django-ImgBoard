from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from .models import *
from .forms import *


# Create your views here.

class CreateConversation(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        ctx = {
            'form': form
        }
        return render(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        try:
            receiver = User.objects.get(username=username)

            if request.user != receiver and Conversation.objects.filter(user=request.user, receiver=receiver).exists():
                conversation = Conversation.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('conversation', pk=conversation.pk)
            
            if form.is_valid():
                sender_conv = Conversation(
                    user = request.user,
                    receiver = receiver
                )

                sender_conv.save()
                conversation.pk = sender_conv.pk
                return redirect('conversation', pk=conversation.pk)
        except User.DoesNotExist:
            return redirect('create-conversation')
        
class ListCoversations(View):
    def get(self, request, *args, **kwargs):
        conv_list = Conversation.objects.filter(Q(user=request.user) | Q(receiver = request.user))
        ctx = {
            'conv_list': conv_list
        }

        return render(request, 'inbox.html', ctx)
    
    class CreateMessage(View):
        def post(self, request, pk, *args, **kwargs):
            conversation = Conversation.objects.get(pk=pk)
            if conversation.receiver == request.user:
                receiver = conversation.user
            else:
                receiver = conversation.receiver
                message = UserMessage(
                    conversation = conversation,
                    sender_user = request.user,
                    receiver_user = receiver,
                    message_text=request.POST.get('body'),
                )
                message.save()
                return redirect('conversation', pk=pk)
            
    class ConversationView(View):
        def get(self, request, pk, *args, **kwargs):
            form = MessageForm()
            conversation = Conversation.objects.get(pk=pk)
            message_list = UserMessage.objects.filter(conversation__pk__contains=pk)
            ctx = {
                'conversation': conversation,
                'form' : form,
                'message_list': message_list
            }

            return render(request, 'conversation.html', ctx)