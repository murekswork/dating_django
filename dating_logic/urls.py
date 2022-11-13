from django.urls import path
from .views import *

urlpatterns = [
    # path('match/<int:action_user_id>/<str:reaction>', LikeView, name='like'),
    path('matches/', MatchesPageView, name='matches'),
    path('profile_likes/', WhoLikedView, name='profile_likes'),
    path('profile_likes/<int:action_user_id>/<str:reaction>/', ReactLikeView, name='react_like'),
    path('dates/', DatesPageView, name='dates'),
    path('messanger/', MessangerView, name='chats'),
    path('/messanger/chat/<int:chat_id>/', ChatView, name='chat'),
    path('', HomePageView, name='home'),
    path('profile/cupid/', cupid_page, name='cupid_page'),
    path('profile/cupid/buy/', cupid_buy_page, name='cupid_buy'),
]