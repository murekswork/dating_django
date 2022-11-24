from django.urls import path
from .views import *

from django.views.decorators.cache import cache_page

urlpatterns = [
    path('gallery/', GalleryPageView.as_view(), name='gallery'),
    path('profile', AccountPageView1.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/setup/', SetupProfileView.as_view(), name='profile_setup'),
    path('profile/<int:image_id>/update/', set_profile_photo_url, name='set_profile_photo'),
    path('profile/<int:pk>/visit/', VisitProfileView.as_view(), name='visit'),
    path('profile/photo/<int:pk>/delete/', profile_delete_photo_view, name='photo_delete')
    # path('', View, name='home'),
]