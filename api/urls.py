from django.urls import path
from rest_framework.authtoken import views

from .views import AccountPageAPIView, GalleryPageAPIView, \
                   SendLikeAPIView, ShowMatchesAPIView, \
                   ChatsAPIView, ChatHistoryAPIView, \
                   ShowLikesAPIView

urlpatterns = [
    path('account_overview/', AccountPageAPIView.as_view()),
    path('gallery_page', GalleryPageAPIView.as_view()),
    path('send_like', SendLikeAPIView.as_view()),
    path('show_matches', ShowMatchesAPIView.as_view()),
    path('chats', ChatsAPIView.as_view()),
    path('chat/<int:pk>/', ChatHistoryAPIView.as_view()),
    path('likes/', ShowLikesAPIView.as_view()),
    path('api-token-auth/', views.obtain_auth_token)

]