from django.contrib import admin
from .models import *

admin.site.register(CustomUserModel)
admin.site.register(Profile)
admin.site.register(ProfilePhotosModel)
# Register your models here.
