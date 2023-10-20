from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from core.models import Profile, Post, LikePost, FollowersCount
from direct_messages.models import *
from itertools import chain
import random, uuid

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    user_posts = Post.objects.filter(user=request.user.username)
    feed.append(user_posts)
    
    feed_list = list(chain(*feed))

    # User suggestions

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    conversations = Conversation.objects.filter(Q(user=request.user) | Q(receiver=request.user)).order_by('-id')[:5]
    last_messages = []
    for conversation in conversations:
        last_message = UserMessage.objects.filter(conversation=conversation).order_by('-message_date').first()
        if last_message:
            last_messages.append(last_message)


    notifications = Notification.objects.filter(to_user=request.user, user_has_seen=False)
    if request.method == 'POST':
        for notification in notifications:
            notification.user_has_seen = True
            notification.save()
        return JsonResponse({'message': 'Notifications marked as seen.'})
    has_unseen_notifications = Notification.objects.filter(to_user=request.user, user_has_seen=False).exists()

    

    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4], 'notifications': notifications, 'last_messages': last_messages, 'has_unseen_notifications': has_unseen_notifications})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def delete(request, pk):
    if request.method == 'POST':
        post = Post.objects.filter(id=pk)

        post.delete()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    to_user = None

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        if isinstance(post.user, User):
            to_user = post.user
        else:
            to_user = User.objects.get(username=post.user)
        notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=to_user, post=post)

        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        Notification.objects.filter(notification_type=1, from_user=request.user, to_user=to_user, post=post).delete()
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
    return render(request, 'settings.html', {'user_profile':user_profile})

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=User.objects.get(username=user))
            return redirect('profile/'+user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

def post_detail(request, id):
    ctx={}
    ctx["post"] = Post.objects.get(id=id)
    return render(request, 'post_detail.html', ctx)

def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user):
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    ctx = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_posts_length' : user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', ctx)

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already registered.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #Log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords do not match.')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    
def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')