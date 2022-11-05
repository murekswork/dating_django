from django.urls import path
from .views import *

urlpatterns = [
    path('gallery/', GalleryPageView, name='gallery'),
    path('profile', AccountPageView, name='profile'),
    path('signup/', SignupView, name='signup'),
    path('profile/setup/', SetupProfileView, name='profile_setup'),
    path('profile/<int:image_id>/update/', set_profile_photo_url, name='set_profile_photo'),
    path('profile/<int:user_id>/visit/', VisitProfileView, name='visit'),
    # path('', View, name='home'),
]