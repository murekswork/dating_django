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
        profile = Profile(user=user, profile_photo=ProfilePhotosModel.objects.get(id=2))
        profile.save(using=self._db)
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name='user_profile')
    hobby = models.CharField(max_length=1024, null=True, blank=True)
    profile_photo = models.ForeignKey('ProfilePhotosModel', null=True, blank=True, on_delete=models.CASCADE, related_name='profile_photo')
    relation_formats = models.TextField(choices=RELATION_FORMATS, default='Looking for sweet daddy!')


    # def new_likes_length(self):
    #     length = find_who_liked_user(self)
    #     return length

    def get_absolute_url(self):
        pass


    def photos(self):
        photos = ProfilePhotosModel.objects.filter(profile=self)
        list_photos = []
        for p in photos:
            list_photos.append(p)
        print(list_photos)
        return list_photos


    def hobbies(self):
        if self.hobby:
            hobby_list = self.hobby.strip('][').split(', ')
            return hobby_list

    def matches(self, matches_model):
        profile_matches = matches_model.filter((Q(user_liker=self)) | Q(user_liked=self))
        return [match for match in profile_matches if match.status == 1]



    def get_likes_length(self):
        from services import find_who_liked_user
        return len(find_who_liked_user(self))

    @classmethod
    def get_profile(cls, user_id):
        return cls.objects.get(user_id=user_id)


    def set_profile_photo(self, photo):
        self.profile = photo

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ProfilePhotosModel(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
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