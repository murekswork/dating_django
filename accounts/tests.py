import sqlite3

import django.db.utils
from django.test import TestCase

from dating_logic.models import Chat, Message, MatchesModel
from .models import CustomUserManager, CustomUserModel, Profile

class CustomUserModelTests(TestCase):

    def test_create_user_admin_status(self):
        '''Test admin admin status'''
        user = CustomUserModel.objects.create_user(email='admincheck@mail.ru', username='admincheck', password='admincheck')
        self.assertEqual(user.is_admin(), False)

    def test_create_user_email(self):
        """Test email"""
        user = CustomUserModel.objects.create_user(email='emailtest@mail.ru', username='emailtest', password='emailtest')
        self.assertEqual(user.email, 'emailtest@mail.ru')

    def test_create_user_password(self):
        """Test password hashing"""
        user = CustomUserModel.objects.create_user(email='passwordcheck@mail.ru', username='passwordcheck', password='passwordcheck@mail.ru')
        self.assertEqual(user.password == 'passwordcheck@mail.ru', False)

    def test_create_user_staff(self):
        """Test user staff status"""
        user = CustomUserModel.objects.create_user(email='admincheck@mail.ru', username='admincheck', password='admincheck')
        self.assertEqual(user.staff, False)

    def test_create_user_superuser(self):
        """Test superuser perm"""
        user = CustomUserModel.objects.create_user(email='admincheck@mail.ru', username='admincheck', password='admincheck')
        self.assertEqual(user.is_superuser, False)

    def test_create_superuser_staff(self):
        """Test superuser staff status"""
        user = CustomUserModel.objects.create_superuser(email='superuser@mail.ru', username='superusercheck',password='superuser')
        self.assertEqual(user.staff, True)

    def test_create_superuser_admin(self):
        """Test superuser admin status"""
        user = CustomUserModel.objects.create_superuser(email='superuser@mail.ru', username='superusercheck',password='superuser')
        self.assertEqual(user.admin, True)

    def test_create_superuser_is_superuser(self):
        """Test superuser staff status"""
        user = CustomUserModel.objects.create_superuser(email='superuser@mail.ru', username='superusercheck',password='superuser')
        self.assertEqual(user.is_superuser, True)


    def test_profile_if_not_user(self):
        """Test if profile can exist without user"""
        with self.assertRaises(django.db.utils.IntegrityError):
            Profile.objects.create()

    def test_profile_get_unread_chats_no_chats(self):
        """Test function get_unread_chats if not unread messages """
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        user2 = CustomUserModel.objects.create(username='User2', email='profil2etest@mail.ru', password='f2asklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile2 = Profile.objects.create(user=user2, last_name='profile2')
        chat = Chat.objects.create(profile1=profile, profile2=profile2)
        self.assertEqual(profile.get_unread_chats(), 0)
        msg1 = chat.send_message(profile=profile2, message_text='Some text')

    def test_profile_get_unread_chats_with_chats(self):
        """Test function get_unread_chats with unread messages"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        user2 = CustomUserModel.objects.create(username='User2', email='profil2etest@mail.ru', password='f2asklaf')
        user3 = CustomUserModel.objects.create(username='User3', email='profil3etest@mail.ru', password='f3asklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile2 = Profile.objects.create(user=user2, last_name='profile2')
        profile3 = Profile.objects.create(user=user3, last_name='profile3')
        chat = Chat.objects.create(profile1=profile, profile2=profile2)
        chat2 = Chat.objects.create(profile1=profile, profile2=profile3)
        self.assertEqual(profile.get_unread_chats(), 0)
        msg1 = chat.send_message(profile=profile2, message_text='Some text')
        msg2 = chat2.send_message(profile=profile3, message_text='Some text')
        self.assertEqual(profile.get_unread_chats(), 2)

    def test_profile_chats_if_other_user_can_send_message_to_chat(self):
        """Test if other user can send message to chat"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        user2 = CustomUserModel.objects.create(username='User2', email='profil2etest@mail.ru', password='f2asklaf')
        user3 = CustomUserModel.objects.create(username='User3', email='profil3etest@mail.ru', password='f3asklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile2 = Profile.objects.create(user=user2, last_name='profile2')
        profile3 = Profile.objects.create(user=user3, last_name='profile3')
        chat = Chat.objects.create(profile1=profile, profile2=profile2)
        self.assertEqual(profile.get_unread_chats(), 0)
        with self.assertRaises(PermissionError):
            msg1 = chat.send_message(profile=profile3, message_text='Some text')

    def test_profile_can_add_cupids(self):
        """Test profile can buy cupid"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile.cupid_transaction(50)
        self.assertEqual(profile.cupid_balance, 50)

    def test_profile_can_spend_cupids(self):
        """Test profile can spend cupid"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile.cupid_transaction(50)
        profile.cupid_transaction(-40)
        self.assertEqual(profile.cupid_balance, 10)

    def test_profile_can_spend_cupids_more_than_current_balance(self):
        """Test if profile try to spend cupids more than current balance"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile.cupid_transaction(50)
        profile.cupid_transaction(-100)
        self.assertEqual(profile.cupid_balance, 50)

    def test_profile_can_pay_premium(self):
        """Test if profile can pay premium with enough money"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile.cupid_transaction(90)
        profile.pay_premium()
        self.assertEqual(profile.vip_status, True)

    def test_profile_can_pay_premium_without_money(self):
        """Test if profile can pay premium with not enough money"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile.cupid_transaction(80)
        profile.pay_premium()
        self.assertEqual(profile.vip_status, False)

    def test_profile_photo(self):
        """Test created profile has not Profile photo set"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        self.assertEqual(profile.profile_photo, None)

    def test_profile_has_matches(self):
        """Test profile matches"""
        user = CustomUserModel.objects.create(username='User1', email='profiletest@mail.ru', password='fasklaf')
        user2 = CustomUserModel.objects.create(username='User2', email='profil2etest@mail.ru', password='f2asklaf')
        user3 = CustomUserModel.objects.create(username='User3', email='profil3etest@mail.ru', password='f3asklaf')
        profile = Profile.objects.create(user=user, last_name='profile1')
        profile2 = Profile.objects.create(user=user2, last_name='profile2')
        profile3 = Profile.objects.create(user=user3, last_name='profile3')
        chat = Chat.objects.create(profile1=profile, profile2=profile2)
        match1 = MatchesModel.objects.create(user_liker=profile2, user_liked=profile, status='1')
        match2 = MatchesModel.objects.create(user_liker=profile3, user_liked=profile, status='1')
        self.assertEqual([match1, match2], profile.matches())















# Create your tests here.
