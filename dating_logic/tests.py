from django.test import TestCase
from accounts.models import CustomUserModel, Profile
from .models import MatchesModel, Chat

class DatingLogicModelsTest(TestCase):

    def test_matches_model_create_match(self):
        user = CustomUserModel.objects.create_user(email='dluser@mail.ru', username='dluser', password='dluser')
        profile = Profile.objects.create(user=user, first_name='Name', last_name='Fullname')
        user1 = CustomUserModel.objects.create_user(email='1dluser@mail.ru', username='1dluser', password='1dluser')
        profile1 = Profile.objects.create(user=user1, first_name='1Name', last_name='1Fullname')

        match = MatchesModel.objects.create(user_liker=profile, user_liked=profile1)
        self.assertEqual(match.user_liker, profile)
        self.assertEqual(match.user_liked, profile1)

    def test_matches_model_create_match_enable_chat(self):
        user = CustomUserModel.objects.create_user(email='dluser@mail.ru', username='dluser', password='dluser')
        profile = Profile.objects.create(user=user, first_name='Name', last_name='Fullname')
        user1 = CustomUserModel.objects.create_user(email='1dluser@mail.ru', username='1dluser', password='1dluser')
        profile1 = Profile.objects.create(user=user1, first_name='1Name', last_name='1Fullname')

        match = MatchesModel.objects.create(user_liker=profile, user_liked=profile1)
        self.assertEqual(match.enable_chat(), True)

        self.assertEqual(match.chat.profile1, profile)
        self.assertEqual(match.chat.profile2, profile1)
        self.assertEqual(match.disable_chat(), False)

    def test_chat_model_create_chat(self):
        user = CustomUserModel.objects.create_user(email='dluser@mail.ru', username='dluser', password='dluser')
        user1 = CustomUserModel.objects.create_user(email='1dluser@mail.ru', username='1dluser', password='1dluser')
        profile1 = Profile(user_id=user.id)
        profile2= Profile(user_id=user1.id)
        # match = MatchesModel.objects.create(user_liker=Profile(user_id=user.id, ), user_liked=Profile(user_id=user1.id))
        chat = Chat.objects.create(profile1=profile1, profile2=profile2)
        print(chat)



# Create your tests here.
