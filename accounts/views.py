from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import SignupForm, ProfileSetupForm, UploadPhotoForm
from .models import *

from services.business_logic import find_all_user_liked, find_who_liked_user


@login_required
def VisitProfileView(request, user_id):
    profile = Profile.get_profile(request.user.id)
    profile_visited = Profile.get_profile(user_id)
    return render(request, template_name='profile_visit.html', context={'profile_visited': profile_visited,
                                                                        'profile': profile,
                                                                        'images': ProfilePhotosModel.objects.filter(profile=profile_visited)})

@login_required
def GalleryPageView(request):
    if request.user.is_authenticated:
        user = Profile.objects.get(user_id=request.user.id)
        profiles = Profile.objects.filter(~Q(gender=user.gender)).filter(~Q(user_id__in=[o.user_id for o in find_all_user_liked(user)])).filter(~Q(user_id__in=[o.user_id for o in find_who_liked_user(user)]))
        context = {'profiles': profiles,
                   'profile': Profile.get_profile(request.user.id),
                   'user_profile': user}
    else:
        return redirect('login')
    return render(request, template_name='home.html', context=context)

@login_required
def AccountPageView(request):
    user = request.user
    profile = Profile.objects.get(user_id=user.id)
    context = {'user': user,
               'profile': profile,
               'form': UploadPhotoForm}
    images = ProfilePhotosModel.objects.filter(profile=profile)
    if images:
        context['images'] = images
    form = UploadPhotoForm()
    if request.method == 'POST':
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                image = form.save(commit=False)
                image.profile = profile
                image.save()
                if not profile.profile_photo:
                    profile.profile_photo = image
                    profile.save()
                context['uploaded_photo'] = image
                messages.add_message(request, messages.SUCCESS, 'Photo successfully uploaded')
            return redirect('profile')
        messages.add_message(request, messages.ERROR, 'Photo was not uploaded')
        form = UploadPhotoForm()
        return redirect('profile')
    return render(request, template_name='profile.html', context = context)


# def UploadPhotoView(request):
#     query_set = {'profile': Profile.objects.get(user_id=request.user.id),
#                  'form': UploadPhotoForm}
#     form = UploadPhotoForm()
#
#     return render(request, template_name='Upload')


@login_required
def SetupProfileView(request):
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                edited_profile = form.save(commit=False)
                edited_profile.user = request.user
                edited_profile.save()
                messages.add_message(request, messages.SUCCESS, 'Profile info saved!')
            return redirect('profile')
        messages.add_message(request, messages.ERROR, 'Invalid input data, try again!')
    form = ProfileSetupForm()
    context = {'user': request.user,
               'profile': request.user.get_profile(),
               'form': ProfileSetupForm}
    return render(request, template_name='profile_setup.html', context=context)


def SignupView(request):
    context = {'form': SignupForm}
    if request.method == 'POST':
        form = SignupForm(request.POST)
        print(request.POST['username'], request.POST['email'], request.POST['password'], 'alpsfk[afk12')
        if form.is_valid():
            print('Form is valid')
            with transaction.atomic():
                new_user = form.save(commit=False)
                new_user.set_password(request.POST['password'])
                new_user.save()

                profile = Profile(user=new_user)
                profile.save()

                new_user.profile = profile
                new_user.save()

                authenticated_user = authenticate(username=new_user.email, password=request.POST['password'])
                login(request, authenticated_user)
            return redirect('profile_setup')
    form = SignupForm()
    return render(request, template_name='registration/signup.html', context=context)
    # context = {'form': UserCreationForm}
    # return render(request, template_name='registration/signup.html', context=)

@login_required
def set_profile_photo_url(request, image_id):
    profile = Profile.objects.get(user_id=request.user.id)
    new_image = ProfilePhotosModel.objects.get(id=image_id)
    profile.profile_photo = new_image
    profile.save()
    messages.add_message(request, messages.SUCCESS, 'Profile photos successfully change')
    return redirect('profile')