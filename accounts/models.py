from _lsprof import profiler_entry
from builtins import classmethod

from django.db import models
from django.db.models import Q

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser
import json


class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, password) -> 'CustomUserModel':
        if not email:
            raise ValueError('User must have email!')
        if not username:
            raise ValueError('User must have username!')
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username):
        superuser = self.create_user(email=email, password=password, username=username)
        superuser.staff = True
        superuser.admin = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class Profile(models.Model):

    RELATION_FORMATS = (
        ('Looking for real love!', 'Looking for real love!'),
         ('Looking for one-night partner!', 'Looking for one-night partner!'),
        ('Looking for sweet daddy!', 'Looking for sweet daddy!'),
        ('Looking for free format relations!', 'Looking for free format relations!')
    )

    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    gender = models.BooleanField(default=True)
    date_of_birth = models.DateField(blank=True, null=True)
    about = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    user = models.OneToOneField("CustomUserModel", primary_key=True, on_delete=models.CASCADE, related_name='user_profile')
    hobby = models.CharField(max_length=1024, null=True, blank=True)
    profile_photo = models.ForeignKey('ProfilePhotosModel', null=True, blank=True, default=None, on_delete=models.SET_DEFAULT, related_name='profile_photo')
    relation_formats = models.TextField(choices=RELATION_FORMATS, default='Looking for sweet daddy!')
    cupid_balance = models.IntegerField(default=0, null=True)
    vip_status = models.BooleanField(default=False)

    def sign_up_welcome_messages(self):
        from dating_logic.models import Chat, MatchesModel, Message
        # welcome_match1 = MatchesModel(user_liker=Profile.objects.get(user__email='bot1@mail.ru'), user_liked=self).save()
        # welcome_match2 = MatchesModel(user_liker=Profile.objects.get(user__email='bot2@mail.ru'), user_liked=self).save()
        welcome_chat1 = Chat.objects.create(profile1=Profile.objects.get(user_id=77), profile2=self)
        welcome_chat2 = Chat.objects.create(profile1=Profile.objects.get(user_id=78), profile2=self)
        welcome_chat1.send_message(profile=Profile.objects.get(user_id=77), message_text='Heeelo sweeeeet!')
        welcome_chat2.send_message(profile=Profile.objects.get(user_id=78), message_text='You are reeeeallly niceee!')
        # welcome_chat1 = welcome_match1.enable_chat().save()
        # welcome_chat2 = welcome_match2.enable_chat().save()
        # welcome_chat1.send_message(profile=Profile.objects.get(email='bot1@mail.ru'), message_text='Hello sweeeeet! :D')
        # welcome_chat2.send_message(profile=Profile.objects.get(email='bot2@mail.ru'), message_text='Do you want to meet up?')


    def get_unread_chats(self):
        # chat_set_one = self.chat_profile_1.select_related()
        # chat_set_two = self.chat_profile_2.select_related()
        # all_chats = chat_set_one.union(chat_set_two)
        from dating_logic.models import Chat, Message
        unread_messages = Message.objects.filter(message_recipient=self, read_status=0)
        print('Unread msg: ',unread_messages)
        # all_chats = Chat.objects.filter(Q(profile1=self) | Q(profile2=self)).only()
        # unread_msg_length = 0
        # for chat in all_chats:
        #     if chat.read_status(request_profile=self) == 'UNREAD':
        #         unread_msg_length += 1
        return len(unread_messages)
    #
    def cupid_transaction(self, amount):
        amount = int(amount)
        if amount > 0:
            self.cupid_balance += amount
            self.save()
        elif amount < 0 and self.cupid_balance >= -amount:
            self.cupid_balance += amount
            self.save()
        return self.cupid_balance

    def pay_premium(self):
        if self.vip_status is False and self.cupid_balance >= 90:
            check_balance = self.cupid_transaction(-90)
            self.vip_status = True
            self.save()
            return {'success': True,
                    'text': 'Premium profile now!'}
        return {'success': False,
                'text': 'Not enough money or already premium'}

    def get_absolute_url(self):
        pass

    def photos(self):
        photos = self.photos()
        return photos

    def hobbies(self):
        if self.hobby:
            hobby_list = self.hobby.strip('][').split(', ')
            return hobby_list

    def matches(self):
        from dating_logic.models import MatchesModel
        profile_matches = MatchesModel.objects.filter((Q(user_liker=self)) | Q(user_liked=self))
        return [match for match in profile_matches if match.status == 1]

    def get_likes_length(self):
        from services.business_logic import find_who_liked_user
        return len(find_who_liked_user(self))

    @classmethod
    def get_profile(cls, user_id):
        return cls.objects.get(user_id=user_id)

    def set_profile_photo(self, photo):
        self.profile = photo

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ProfilePhotosModel(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.SET_DEFAULT, related_name='photos', default=None, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='images/users/')


class CustomUserModel(AbstractUser):

    objects = CustomUserManager()
    username = models.CharField(max_length=255, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    registration_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_profile(self):
        return Profile.objects.get(user_id=self.id)

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.admin

    def is_staff(self):
        return self.staff

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perm(self, perm, app_label):
        return True