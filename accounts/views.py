from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views.generic import ListView, TemplateView, View, DetailView, FormView

from config.settings import AUTH_USER_MODEL
from django.conf import settings

from .forms import SignupForm, ProfileSetupForm, UploadPhotoForm
from .models import *
from dating_logic.models import ProfileGiftTable

from services.business_logic import find_all_user_liked, like_someone, find_who_liked_user
from services import business_logic


class VisitProfileView(DetailView):
    model = Profile
    context_object_name = 'profile_visited'
    template_name = 'profile_visit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.user_profile
        context['gifts'] = ProfileGiftTable.objects.filter(profile_receiver=context['profile'])
        return context

    def get_queryset(self):
        return Profile.objects.filter(user_id=self.kwargs['pk'])




# @login_required
# def VisitProfileView(request, user_id):
#     profile = request.user.user_profile
#     profile_visited = Profile.get_profile(user_id)
#     return render(request, template_name='profile_visit.html', context={'profile_visited': profile_visited,
#                                                                         'profile': profile,
#                                                                         'images': ProfilePhotosModel.objects.filter(profile=profile_visited)})

# class GalleryPageView(ListView):
#     template_name = 'home.html'
#     model = Profile
#     context_object_name = 'profiles'
#
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['profile'] = self.request.user.user_profile
#         return context
#
#
#
#
#     def get_queryset(self):
#         return Profile.objects.filter(~Q(gender=self.request.user.user_profile.gender)).filter(~Q(user_id__in=[o.user_id for o in find_all_user_liked(self.request.user.user_profile)])).filter(~Q(user_id__in=[o.user_id for o in find_who_liked_user(self.request.user.user_profile)]))

@login_required
def GalleryPageView(request):
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user_id=request.user.id)
        profiles = Profile.objects.filter(~Q(gender=user_profile.gender)).filter(~Q(user_id__in=[o.user_id for o in find_all_user_liked(user_profile)])).filter(~Q(user_id__in=[o.user_id for o in find_who_liked_user(user_profile)]))
        context = {'profiles': profiles,
                   'profile': user_profile,
                   }

        if 'like' in request.POST:
            action_user_id = request.POST.get('like')
            message = like_someone(user_profile, action_user_id=action_user_id, reaction='like')
            messages.add_message(request, messages.SUCCESS, message=message['message'])

    else:
        return redirect('login')
    return render(request, template_name='home.html', context=context)


# class AccountPageView(FormView):
#
#     template_name = 'profile.html'
#     form_class = UploadPhotoForm
#     success_url = 'profile'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['profile'] = self.request.user.user_profile
#         return context
#
#     def form_valid(self, form):
#         image = form.save(commit=False)
#         image.profile = self.request.user.user_profile
#         image.save()
#
#     def form_invalid(self, form):
#         return self.form_class



@login_required
def AccountPageView(request):
    user = request.user
    user_profile = request.user.user_profile
    context = {'user': user,
               'profile': user_profile,
               'form': UploadPhotoForm,
               'gifts': ProfileGiftTable.objects.filter(profile_receiver=user_profile)}
    form = UploadPhotoForm()
    if request.method == 'POST':
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                image = form.save(commit=False)
                image.profile = user_profile
                image.save()
                if not user_profile.profile_photo:
                    user_profile.profile_photo = image
                    user_profile.save()
                context['uploaded_photo'] = image
                messages.add_message(request, messages.SUCCESS, 'Photo successfully uploaded')
            return redirect('profile')
        messages.add_message(request, messages.ERROR, 'Photo was not uploaded')
        form = UploadPhotoForm()
        return redirect('profile')
    return render(request, template_name='profile.html', context = context)


def UploadPhotoView(request):
    query_set = {'profile': Profile.objects.get(user_id=request.user.id),
                 'form': UploadPhotoForm}
    form = UploadPhotoForm()

    return render(request, template_name='Upload')


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
        if form.is_valid():
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
    profile = request.user.user_profile
    new_image = ProfilePhotosModel.objects.get(id=image_id)
    profile.profile_photo = new_image
    profile.save()
    messages.add_message(request, messages.SUCCESS, 'Profile photos successfully change')
    return redirect('profile')