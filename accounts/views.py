from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views.generic import ListView, TemplateView, View, DetailView, FormView

from config.settings import AUTH_USER_MODEL
from django.conf import settings

from services.utils import ExcludedProfilesMixin
from .forms import SignupForm, ProfileSetupForm, UploadPhotoForm
from .models import *
from dating_logic.models import Message, Chat, Gift, MatchesModel
from dating_logic.models import ProfileGiftTable

from services.business_logic import find_all_user_liked, like_someone, find_who_liked_user
from services import business_logic, utils


class VisitProfileView(utils.DataMixin, utils.LoginRequiredMixin, DetailView):
    model = Profile
    context_object_name = 'profile_visited'
    template_name = 'profile_visit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_visited'] = Profile.objects.get(user_id=self.kwargs['pk'])
        context['gifts'] = ProfileGiftTable.objects.filter(profile_receiver=context['profile_visited'])
        extra_context = self.get_user_context()
        return dict(list(context.items()) + list(extra_context.items()))





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
def get_unread_chats(request_profile):
    chat_set_one = request_profile.chat_profile_1.select_related()
    chat_set_two = request_profile.chat_profile_2.select_related()
    all_chats = chat_set_one.union(chat_set_two)
    print(all_chats)
    unread_msg_length = 0
    for chat in all_chats:
        if  chat.read_status(request_profile) == 'UNREAD':
            print('PLUS ONE')
            unread_msg_length += 1
        else:
            print('-ONE')
    return unread_msg_length


class GalleryPageView(utils.DataMixin, ExcludedProfilesMixin, utils.ProfileSetupedMixin, utils.LoginRequiredMixin, ListView):
    template_name = 'home.html'
    model = Profile
    context_object_name = 'profiles'
    paginate_by = 8


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        extra_context = self.get_user_context()
        return dict(list(context.items()) + list(extra_context.items()))




    # def get_queryset(self):
    #     excluded_profiles = list(find_all_user_liked(self.request.user.user_profile) + find_who_liked_user(self.request.user.user_profile))
    #     Profile.objects.all().exclude(user_id__in=[user.user_id for user in excluded_profiles])

    def post(self, request,  *args, **kwargs):
        action_user_id = request.POST.get('like')
        like = like_someone(request.user.user_profile, action_user_id=action_user_id, reaction='like')
        messages.add_message(request, messages.SUCCESS, message=like['message'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def GalleryPageV1iew(request):
    if request.user.is_authenticated:
        user_profile = request.user.user_profile
        profiles = Profile.objects.filter(~Q(gender=user_profile.gender)).\
            filter(~Q(user_id__in=[o.user_id for o in find_all_user_liked(user_profile)])).\
            filter(~Q(user_id__in=[o.user_id for o in find_who_liked_user(user_profile)]))
        context = {'profiles': profiles,
                   'profile': user_profile,
                   'unread_messages': user_profile.get_unread_chats()}
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


# class AccountPageView(FormView):
#     form_class = UploadPhotoForm
#     template_name = 'profile.html'
#     success_url = '/gallery/'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = self.request.user
#         context['profile'] = context['user'].user_profile
#         context['form'] = UploadPhotoForm
#         context['gifts'] = ProfileGiftTable.objects.filter(profile_receiver=context['profile'])
#         context['unread_messages'] = context['profile'].get_unread_chats()
#         return context
#
#     def get(self, request, *args, **kwargs):
#         form = UploadPhotoForm
#         return form
#     def post(self, request, *args, **kwargs):
#         pass
#
#     def form_valid(self, form):
#         with transaction.atomic():
#             image = form.save()
#             image.profile = self.kwargs['profile']
#             image.save()
#             if not self.kwargs['profile'].profile_photo:
#                 self.kwargs['profile'].profile_photo = image
#                 self.kwargs['profile'].save()
#                 self.kwargs['uploaded_photo'] = image
#         return super().form_valid(form)

class AccountPageView(utils.DataMixin, utils.LoginRequiredMixin, View):

    def get(self, request):
        context = self.get_user_context()
        form = UploadPhotoForm()
        context['form'] = form
        context['gifts'] = ProfileGiftTable.objects.filter(profile_receiver=context['profile'])

    def post(self, request):
        form = UploadPhotoForm(request.POST)
        if form.is_valid():
            image = form.save(commit=False)
            image.profile = request.user.user_profile
            image.save()
            request.user.user_profile.profile_photo = image
            request.user.user_profile.save()


class AccountPageView1(utils.DataMixin, utils.LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    context_object_name = 'profile'
    model = Profile
    form = UploadPhotoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_user_context()
        context = dict(list(context.items()) + list(extra_context.items()))
        context['gifts'] = context['profile'].gift_receiver.select_related()
        return context
    
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = self.form()
        return render(request, template_name=self.template_name, context=context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.profile = context['profile']
            image.save()

            context['profile'].profile_photo = image
            context['profile'].save()
            messages.add_message(request, messages.SUCCESS, 'Profile photo added!')
        else:
            print('FORM IS INVALID')
        return redirect('profile')

# @login_required
# def AccountPageView(request):
#     user = request.user
#     user_profile = request.user.user_profile
#     context = {'user': user,
#                'profile': user_profile,
#                'form': UploadPhotoForm,
#                'gifts': ProfileGiftTable.objects.filter(profile_receiver=user_profile),
#                'unread_messages': user_profile.get_unread_chats()}
#
#     form = UploadPhotoForm()
#     if request.method == 'POST':
#         form = UploadPhotoForm(request.POST, request.FILES)
#         if form.is_valid():
#             with transaction.atomic():
#                 image = form.save(commit=False)
#                 image.profile = user_profile
#                 image.save()
#                 if not user_profile.profile_photo:
#                     user_profile.profile_photo = image
#                     user_profile.save()
#                 context['uploaded_photo'] = image
#                 messages.add_message(request, messages.SUCCESS, 'Photo successfully uploaded')
#             return redirect('profile')
#         messages.add_message(request, messages.ERROR, 'Photo was not uploaded')
#         form = UploadPhotoForm()
#         return redirect('profile')
#     return render(request, template_name='profile.html', context = context)


def UploadPhotoView(request):
    query_set = {'profile': Profile.objects.get(user_id=request.user.id),
                 'form': UploadPhotoForm}
    form = UploadPhotoForm()

    return render(request, template_name='Upload')


# @login_required
# def SetupProfileView(request):
#     if request.method == 'POST':
#         form = ProfileSetupForm(request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 edited_profile = form.save(commit=False)
#                 edited_profile.user = request.user
#                 edited_profile.save()
#                 messages.add_message(request, messages.SUCCESS, 'Profile info saved!')
#             return redirect('profile')
#         messages.add_message(request, messages.ERROR, 'Invalid input data, try again!')
#     form = ProfileSetupForm()
#     context = {'user': request.user,
#                'profile': request.user.get_profile(),
#                'form': ProfileSetupForm}
#     return render(request, template_name='profile_setup.html', context=context)

class SetupProfileView(utils.DataMixin, utils.LoginRequiredMixin, FormView):

    template_name = 'profile_setup.html'
    form_class = ProfileSetupForm
    success_url = '/profile'


    def form_valid(self, form):
        self.request.user.user_profile = form.save(commit=False)
        self.request.user.user_profile.user_id = self.request.user.id
        self.request.user.user_profile.save()
        messages.add_message(self.request, messages.SUCCESS, 'Profile info saved!')
        return redirect('profile')

    def form_invalid(self, form):
        super().form_invalid(form)
        messages.add_message(self.request, messages.WARNING, f"Invalid fields data!")
        return redirect('profile_setup')

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        initial_data = {'first_name': context['profile'].first_name,
                        'last_name': context['profile'].last_name,
                        'gender': context['profile'].gender,
                        'date_of_birth': context['profile'].date_of_birth,
                        'city': context['profile'].city,
                        'about': context['profile'].about,
                        'hobbies': context['profile'].hobby,
                        'relation_format': context['profile'].relation_formats
                        }
        form = self.form_class(initial=initial_data)
        context['form'] = form
        return render(self.request, 'profile_setup.html', context)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = self.get_user_context()
        return dict(list(context.items()) + list(extra_context.items()))

# class SetupProfileView(View):
#
#     def get(self, request):
#         form = ProfileSetupForm()
#         context = {'user': request.user,
#                    'profile': request.user.user_profile,
#                    'form': form}
#         return render(request, 'profile_setup.html', context)
#
#     def post(self, request):
#         form = ProfileSetupForm(request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 edited_profile = form.save(commit=False)
#                 edited_profile.user = request.user
#                 edited_profile.save()
#                 messages.add_message(request, messages.SUCCESS, 'Profile info saved!')
#             return redirect('profile')

class SignUpView(View):
    def get(self, request):
        form = SignupForm()
        context = {'form': form}
        return render(request, 'registration/signup.html', context=context)

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                new_user = form.save(commit=False)
                new_user.set_password(request.POST['password'])
                new_user.save()

                authenticated_user = authenticate(username=new_user.email, password=request.POST['password'])
                login(request, authenticated_user)

                new_user_profile = Profile(user=new_user)
                new_user_profile.save()
                new_user_profile.sign_up_welcome_messages()
            welcome_message(request_profile=request.user.user_profile)
            return redirect('profile_setup')
        return redirect('signup')


def welcome_message(request_profile):
    admin_girl_profile = Profile.objects.get(user_id='3')
    welcome_chat = Chat(profile1=admin_girl_profile, profile2=request_profile)
    welcome_chat.save()
    welcome_chat.send_message(message_text=f'{request_profile} you are welcome! I advice you to buy premium status!',
                              profile=admin_girl_profile)
    welcome_gift = ProfileGiftTable(profile_sender=admin_girl_profile, profile_receiver=request_profile, gift=Gift.objects.get(name='welcome-gift'))
    welcome_gift.save()
    welcome_chat.send_message(message_text='', profile=admin_girl_profile, message_gift=welcome_gift)


def profile_delete_photo_view(request, pk: ProfilePhotosModel):
    photo = ProfilePhotosModel.objects.get(id=pk)
    if photo.profile == request.user.user_profile:
        photo.delete()
        messages.add_message(request, messages.SUCCESS, f'Photo successfully deleted')
    else:
        messages.add_message(request, messages.WARNING, f'Its not yours!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# def SignupView(request):
#     context = {'form': SignupForm}
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 new_user = form.save(commit=False)
#                 new_user.set_password(request.POST['password'])
#                 new_user.save()
#
#                 profile = Profile(user=new_user)
#                 profile.save()
#
#                 new_user.profile = profile
#                 new_user.save()
#
#                 authenticated_user = authenticate(username=new_user.email, password=request.POST['password'])
#                 login(request, authenticated_user)
#             return redirect('profile_setup')
#     form = SignupForm()
#     return render(request, template_name='registration/signup.html', context=context)
#     # context = {'form': UserCreationForm}
#     # return render(request, template_name='registration/signup.html', context=)

@login_required
def set_profile_photo_url(request, image_id):
    profile = request.user.user_profile
    new_image = ProfilePhotosModel.objects.get(id=image_id)
    profile.profile_photo = new_image
    profile.save()
    messages.add_message(request, messages.SUCCESS, 'Profile photos successfully change')
    return redirect('profile')