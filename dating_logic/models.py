import datetime

from django.db import models
from accounts.models import *
from django.contrib import messages


class MatchesModel(models.Model):
    user_liker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='liker')
    user_liked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='liked')
    user_liker_like = models.BooleanField(null=True, blank=True)
    user_liked_like = models.BooleanField(null=True, blank=True)
    # status(0) - nothing,
    # status(1) - match,
    # status(2) - someone disliked
    status = models.IntegerField(default=0)
    chat_function = models.BooleanField(default=False)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user_liker} + {self.user_liked}'

    # def like(self, who_likes):
    #     if who_likes == 'liker':
    #         if not self.user_liker_like:
    #             self.user_liker_like = True
    #             self.save()
    #     else:
    #         if not self.user_liked_like:
    #             self.user_liked_like = True
    #             self.save()
    #     self.check_match()
    #     return {f'{self.user_liker}': self.user_liker_like,
    #             f'{self.user_liked}': self.user_liked_like}
    #
    # def dislike(self, who_dislikes):
    #     if who_dislikes == 'liker':
    #         self.user_liker_like = False
    #         self.status = 2
    #         self.save()
    #     else:
    #         self.user_liked_like = False
    #         self.status = 2
    #         self.save()
    #     return {f'{self.user_liker}': self.user_liker_like,
    #             f'{self.user_liked}': self.user_liked_like}

    def check_match(self):
        if (self.user_liked_like==True) and (self.user_liker_like==True):
            self.status = 1
            self.enable_chat()
            self.save()
        elif (self.user_liked_like==0) or (self.user_liker_like==0):
            self.status = 2
            self.save()
        return self.status

    def enable_chat(self):
        self.chat_function = True
        self.chat = Chat(profile1=self.user_liker, profile2=self.user_liked)
        self.chat.save()
        return self.chat

    def disable_chat(self):
        self.chat_function = False
        self.save()
        return self.chat_function


class Message(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='chat_messages')
    read_status = models.BooleanField(default=False, null=False, blank=False)
    send_time = models.DateTimeField(auto_now_add=True)
    message_sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='message_sender')
    message_recipient = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE, related_name='message_recipient')
    message_text = models.CharField(max_length=2048, blank=True, null=True)
    message_gift = models.ForeignKey('ProfileGiftTable', null=True, blank=True, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.send_time)

class Chat(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='chat_profile_1')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='chat_profile_2')
    newest_message_time = models.DateTimeField(blank=True, null=True)

    def read_status(self, request_profile):
        last_message = Message.objects.filter(chat_id=self.id).exclude(message_sender=(request_profile)).last()
        if last_message:
            if last_message.read_status == 0:
                return 'UNREAD'
            else:
                return 'READ'
        return 'Not message'



    def chat_profile(self, profile):
        if self.profile1 != profile:
            print(self.profile1, 'AKFPOKAS')
            return self.profile1
        else:
            print(self.profile2, 'AKPFKSPFO')
            return self.profile2


    def get_chat_receiver(self, request_profile):
        profiles = [self.profile1, self.profile2]
        profiles.remove(request_profile)
        return profiles[0]

    def get_chat_messages(self):
        messages = Message.objects.order_by('-send_time').filter(chat=self)
        return messages

    def send_message(self, profile: Profile, message_text, message_gift: "ProfileGiftTable" = None) -> Message:
        if profile in [self.profile1, self.profile2]:
            message = Message(chat=self, message_sender=profile, message_recipient=self.chat_profile(profile), message_text=message_text, message_gift=message_gift)
            message.save()
            self.newest_message_time = datetime.datetime.now()
            self.save()
            return message
        else:
            raise PermissionError

    def send_gift(self, profile: Profile, gift_id: "Gift"):
        receiver = self.get_chat_receiver(request_profile=profile)
        gift = Gift.objects.get(id=gift_id)

        if not profile.cupid_balance >= gift.price:
            return {'success': False,
                    'text': 'Not enough cupids!'}

        profile.cupid_transaction(amount=-gift.price)
        sent_gift = ProfileGiftTable(profile_sender=profile, profile_receiver=receiver, gift=gift)
        sent_gift.save()
        self.send_message(profile=profile, message_text='Gift', message_gift=sent_gift)
        sent_gift.save()
        return {'success': True,
                'text': f'{profile} sent {gift} to {receiver}!'}


    @classmethod
    def get_user_chats(cls, profile):
        chats = cls.objects.filter(profile1=profile) | cls.objects.filter(profile2=profile)
        return chats

    def __str__(self):
        return f'{self.profile1} | {self.profile2}'


class Gift(models.Model):
    name = models.CharField(max_length=50, default='Gift name')
    gift_image = models.ImageField(upload_to='gifts/', blank=True, null=True)
    price = models.IntegerField(default=5)

    def __str__(self):
        return self.name


class ProfileGiftTable(models.Model):
    profile_sender = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name='gift_sender')
    profile_receiver = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name='gift_receiver')
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, null=True, blank=True)
    text_card = models.TextField(null=True, blank=True, default='All the best!')
    gift_time = models.DateField(auto_now_add=True)




# Create your models here.
