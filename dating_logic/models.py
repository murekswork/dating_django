from django.db import models
from accounts.models import *
from django.contrib import messages


class MatchesModel(models.Model):
    user_liker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='LIKER')
    user_liked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='LIKED')
    user_liker_like = models.BooleanField(null=True, blank=True)
    user_liked_like = models.BooleanField(null=True, blank=True)
    # status(0) - nothing,
    # status(1) - match,
    # status(2) - someone disliked
    status = models.IntegerField(default=0)
    chat_function = models.BooleanField(default=False)

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
        return self.chat_function

    def disable_chat(self):
        self.chat_function = False
        return self.chat_function

# Create your models here.
