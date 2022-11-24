from django.urls import path
from .views import *

from django.views.decorators.cache import cache_page



urlpatterns = [
    # path('match/<int:action_user_id>/<str:reaction>', LikeView, name='like'),
    path('matches/', MatchesPageView.as_view(), name='matches'),
    path('profile_likes/', WhoLikeView.as_view(), name='profile_likes'),
    path('profile_likes/<int:action_user_id>/<str:reaction>/', ReactLikeView.as_view(), name='react_like'),
    path('dates/', DatesPageView.as_view(), name='dates'),
    path('messanger/', MessangerPageView.as_view(), name='chats'),
    path('/messanger/chat/<int:chat_id>/', ChatPageView.as_view(), name='chat'),
    path('/messanger/chat/<int:chat_id>/sendgift/<int:gift_id>/', send_chat_gift_view, name='send_message_gift'),
    path('/messanger/chat/<int:chat_id>/delete', delete_chat_view, name='chat_delete'),
    path('', HomePageView, name='home'),
    path('profile/cupid/', cache_page(10)(CupidPageView.as_view()), name='cupid_page'),
    path('profile/cupid/buy/', CupidBuyPage.as_view(), name='cupid_buy'),
]