from django.urls import path
from .views import *

urlpatterns = [
    path('match/<int:user2>/<str:reaction>', LikeView, name='like'),
    path('matches/', MatchesPageView, name='matches'),
    path('dates/', DatesPageView, name='dates'),
    path('', HomePageView, name='home'),
]