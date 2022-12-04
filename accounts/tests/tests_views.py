import json

from django.contrib.auth import authenticate, login, get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import CustomUserModel, Profile
from accounts.views import AccountPageView1
from dating_logic.models import Message, Chat


class AccountPageTest(TestCase):

    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(username='temporary', email='temporary@gmail.com', password='temporary')
        profile = Profile.objects.create(user=user, first_name='name', last_name='lname')
        self.client.login(username='temporary@gmail.com', password='temporary')

    def test_status_code_200(self):
        User = get_user_model()
        response = self.client.get('/profile', follow=True)
        user = User.objects.get(username='temporary')
        profile = user.user_profile
        self.assertEqual(response.status_code, 200)

    def test_ContextData_user(self):
        """ Check if user in response context"""
        User = get_user_model()
        response = self.client.get('/profile', follow=True)
        user = User.objects.get(username='temporary')
        self.assertEqual(response.context['user'], user)

    def test_ContextData_profile(self):
        """ Check if user in response context"""
        User = get_user_model()
        response = self.client.get('/profile', follow=True)
        user = User.objects.get(username='temporary')
        profile = Profile.objects.get(user=user)
        self.assertEqual(response.context['profile'], profile)

    def test_ContextData_unread_messages(self):
        """ Check if unread messages in response context"""
        User = get_user_model()
        user = User.objects.get(username='temporary')
        profile = Profile.objects.get(user=user)
        chat = Chat.objects.create(profile1=profile, profile2=profile)
        message1 = Message.objects.create(chat=chat, message_sender=profile, message_recipient=profile,
                                          message_text='Hello', read_status=0)
        message2 = Message.objects.create(chat=chat, message_sender=profile, message_recipient=profile,
                                          message_text='Hel3lo', read_status=0)
        message3 = Message.objects.create(chat=chat, message_sender=profile, message_recipient=profile,
                                          message_text='Hel2lo', read_status=0)

        response = self.client.get('/profile', follow=True)
        self.assertEqual(response.context['unread_messages'], 3)
        # self.assertEqual(response.context['unread_messages'], )