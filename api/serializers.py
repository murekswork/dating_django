from rest_framework.serializers import ModelSerializer

from accounts.models import Profile
from dating_logic.models import MatchesModel, Chat, Message


class ProfileSerializer(ModelSerializer):

    class Meta:
        model = Profile
        exclude = ['cupid_balance', 'vip_status', 'user']


class MatchesSerializer(ModelSerializer):

    class Meta:
        model = MatchesModel
        fields = '__all__'


class SendLikeSerializer(ModelSerializer):

    class Meta:
        model = MatchesModel
        fields = ['user_liked', 'id']


class ChatsSerializer(ModelSerializer):

    class Meta:
        model = Chat
        fields = '__all__'


class MessagesSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

