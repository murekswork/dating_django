from django.contrib import admin
from .models import Chat, Message, Gift, ProfileGiftTable

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Gift)
admin.site.register(ProfileGiftTable)

# Register your models here.
