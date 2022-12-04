from django.http import request
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from dating_logic.models import *
from accounts.models import *

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.core.cache import cache

class LoginRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'


class DataMixin:

    def get_user_context(self, **kwargs):
        kwargs['user'] = self.request.user
        kwargs['profile'] = kwargs['user'].user_profile
        kwargs['unread_messages'] = kwargs['profile'].get_unread_chats()
        return kwargs


class ExcludedProfilesMixin:

    def get_queryset(self, *kwargs):
        profile = self.request.user.user_profile
        exclude_liked = MatchesModel.objects.filter(~Q(user_liked=profile)).values('user_liker__user_id')
        exclude_liker = MatchesModel.objects.filter(~Q(user_liker=profile)).values('user_liked__user_id')

        return Profile.objects.all().exclude(user_id__in=(exclude_liker.union(exclude_liked)))


class ProfileSetupedMixin(UserPassesTestMixin):

    def handle_no_permission(self):
        return redirect('profile')

    def test_func(self):
        profile = self.request.user.user_profile
        if not profile.first_name or not profile.last_name or not profile.profile_photo or not profile.relation_formats:
            messages.add_message(self.request, messages.WARNING, 'You must setup your profile including profile photo before start!')
            return False
        return True

    # if not cache.get('user'):
        #     cached_user = self.request.user
        #     cache.set('user', cached_user, 200)
        #     context['user'] = cache.get('user')
        # else:
        #     context['user'] = cache.get('user')
        #
        # if not cache.get('profile'):
        #     cache.set('profile', Profile.objects.get(user_id=cache.get('user').id), 200)
        #     context['profile'] = cache.get('profile')
        # else:
        #     context['profile'] = cache.get('profile')
        #
        # if not cache.get('unread_messages'):
        #     cache.set('unread_messages', cache.get('profile').get_unread_chats(), 200)
        #     context['unread_messages'] = cache.get('unread_messages')
        # else:
        #     context['unread_messages'] = cache.get('unread_messages')

    # def get_user_context(self, **kwargs):
    #     context = kwargs
    #
    #     context['user'] = self.request.user
    #     context['profile'] = context['user'].user_profile
    #     context['unread_messages'] = context['profile'].get_unread_chats()
    #
    #     return context