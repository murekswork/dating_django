import random
import time

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from accounts.models import Profile, CustomUserModel
from .models import MatchesModel, Chat, Message, Gift
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.paginator import Paginator
from django.db import transaction
from django.views import View


from services.utils import *
from services.business_logic import find_match_between_profiles, \
                                    find_all_user_liked, \
                                    first_like_or_dislike, \
                                    find_who_liked_user, react_like, like_someone


def HomePageView(request):
    if request.user.is_authenticated:
        return redirect('gallery')
    else:
        return redirect('login')


# @login_required
# def LikeView(request, action_user_id, reaction):
#     request_profile = request.user.user_profile
#     action_profile: Profile = Profile.get_profile(user_id=action_user_id)
#
#     already_liked_list = find_all_user_liked(Drequest_profile)
#
#     if action_profile not in already_liked_list:
#         first_like_or_dislike(request_profile, action_profile, reaction)
#         messages.add_message(request, messages.INFO, f'You successfully {reaction}d {action_profile}')
#
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class WhoLikeView(LoginRequiredMixin, DataMixin, ListView):

    model = Profile
    template_name = 'profile_likes.html'
    context_object_name = 'likes'


    def get_context_data(self, *args, **kwargs):
        context = self.get_user_context()
        context['likes'] = MatchesModel.objects.filter(Q(user_liked=self.request.user.user_profile) & Q(status=0))
        return context

    def get_queryset(self, **kwargs):
        context = self.get_context_data()
        res = MatchesModel.objects.filter(Q(user_liked=self.request.user.user_profile) & Q(status=0))
        return res

    def post(self, *args, **kwargs):
        reaction = ''
        if 'like' in self.request.POST:
            reaction = 'like'
        else: reaction = 'dislike'
        match = MatchesModel.objects.get(id=self.request.POST.get(reaction))

        result = react_like(profile1=match.user_liked, profile2=match.user_liker, reaction=reaction)
        messages.add_message(self.request, messages.INFO, f'{result["text"]}')

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))








@login_required
def WhoLikedView1(request):
    profile = Profile.get_profile(user_id=request.user.id)
    # who_liked_list = find_who_liked_user(profile=profile)
    matches_list = MatchesModel.objects.filter(Q(user_liked=profile) & Q(status=0))

    context = {'profile': profile,
               'likes': matches_list,
               'unread_messages': profile.get_unread_chats()}

    if 'like' in request.POST:
        match: MatchesModel = MatchesModel.objects.get(id=request.POST.get('like'))
        match.enable_chat()
        match.status = 1
        match.save()
        time.sleep(1.5)
        messages.add_message(request, messages.SUCCESS, message=f'Match! Now you can chat with {match.user_liked}')

    if 'dislike' in request.POST:
        match: MatchesModel = MatchesModel.objects.get(id=request.POST.get('dislike'))
        match.disable_chat()
        match.status = 2
        match.save()
        time.sleep(1.5)
        messages.add_message(request, messages.SUCCESS, message=f'Dislike! {match.user_liked} user blocked...')

    return render(request, template_name='profile_likes.html', context=context)


class MessangerPageView(DataMixin, LoginRequiredMixin, ListView):

    model = Chat
    context_object_name = 'chats'

    def get(self, *args, **kwargs):
        context = self.get_user_context()
        chats = Chat.get_user_chats(profile=context['profile']).order_by('-newest_message_time')
        chats_with_profile_dict = []
        for chat in chats:
            # chat_profile = chat.chat_profile(context['profile'])
            for i in [chat.profile1, chat.profile2]:
                if i != context['profile']:
                    chat_profile = i
            chat_read_status = ''

            chat_read_status = chat.read_status(context['profile'])
            # try:
            #     last_message = chat.chat_messages.filter(message_sender=chat_profile).last().read_status
            #     if last_message == '1':
            #         chat_read_status = 'READ'
            #     elif last_message == '0':
            #         chat_read_status = 'UNREAD'
            # except:
            #     pass

            chats_with_profile_dict.append({'chat': chat,
                                            'chat_profile': chat_profile,
                                            'chat_read_status': chat_read_status})

        context['chats'] = chats_with_profile_dict
        return render(self.request, 'messanger.html', context=context)

    def post(self, *ars, **kwargs):
        chat_id = self.request.POST.get('chat_id')
        return redirect('chat', chat_id=chat_id)

@login_required
def MessangerView(request):


    profile = Profile.get_profile(user_id=request.user.id)
    chats = Chat.get_user_chats(profile=profile)

    chats_with_profile_dict = []

    for chat in chats:
        chat_profile = chat.chat_profile(profile)
        chat_read_status = ''

        try:
            last_message = chat.chat_messages.filter(message_sender=chat_profile).last().read_status
            if last_message == '1':
                chat_read_status = 'READ'
            elif last_message == '0':
                chat_read_status = 'UNREAD'
        except: pass

        chats_with_profile_dict.append({'chat':chat,
                                         'chat_profile': chat_profile,
                                        'chat_read_status': chat_read_status})

    if not profile.vip_status:
        chats_with_profile_dict = chats_with_profile_dict[:2]
    context = {'profile': profile,
               'chats': chats_with_profile_dict}

    if 'chat_id' in request.POST:
        chat_id = request.POST.get('chat_id')
        chat = Chat.objects.get(id=chat_id)
        selected_chat_messages = chat.get_chat_messages()
        chat_receiver = chat.get_chat_receiver(profile)
        return redirect('chat', chat_id=int(chat_id))


    return render(request, template_name='messanger.html', context=context)

def check_chat_access(request_profile, chat: Chat):
    if not request_profile in [chat.profile1, chat.profile2]:
        return {'success': 'denied'}
    return {'success': 'allowed'}


class ChatPageView(LoginRequiredMixin, ProfileSetupedMixin , DataMixin, ListView):
    model = Message
    template_name = 'chat.html'
    paginate_by = 8
    context_object_name = 'chat_messages'


    def get_context_data(self, *args, **kwargs):

        queryset = kwargs.pop('object_list', None)
        if queryset is None:
            self.object_list = Chat.objects.get(id=self.kwargs['chat_id']).get_chat_messages()


        self.object_list.update(read_status=1)
        paginator = Paginator(self.object_list, self.paginate_by)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)


        context = super().get_context_data(**kwargs)
        extra_context = self.get_user_context()
        context = dict(list(context.items()) + list(extra_context.items()))
        context['chat_messages'] = reversed(page_obj)

        context['chat'] = Chat.objects.get(id=self.kwargs['chat_id'])
        context['chat_id'] = self.kwargs['chat_id']
        context['chat_receiver'] = context['chat'].get_chat_receiver(request_profile=context['profile'])
        return context





    # def get(self, *args, **kwargs):
    #     self.kwargs['chat'].chat_messages.filter(~Q(message_sender=self.kwargs['profile'])).update(read_status=1)
    #     return render(self.request, self.template_name, self.get_context_data())
    # def get_queryset(self, **kwargs):
    #     return Chat.objects.get(id=self.kwargs['chat_id']).get_chat_messages()

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if 'message_text' in request.POST:
            context['chat'].send_message(context['profile'], request.POST.get('message_text'))

        elif 'message_gift' in request.POST:
            context['gift_list'] = Gift.objects.all()

        return render(request, self.template_name, context=context)


    # def get(self, *args, **kwargs):
    #     context = self.get_context_data()
    #     chat = Chat.objects.get(id=kwargs['chat_id'])
    #     context['chat_receiver'] = chat.get_chat_receiver(r q equest_profile=context['profile'])
    #     context['chat_messages'] = self.page_kwarg
    #     return render(self.request, template_name='chat.html', context=context)
@login_required
def ChatVie1w(request, chat_id):
    profile = request.user.user_profile
    chat = get_object_or_404(Chat, id=chat_id)

    if not check_chat_access(profile, chat)['success'] == 'allowed':
        messages.add_message(request, messages.WARNING, 'Access denied')
        return HttpResponseNotFound(request)

    chat_receiver = chat.get_chat_receiver(profile)
    chat_messages = chat.get_chat_messages()
    chat.chat_messages.filter(~Q(message_sender=profile)).update(read_status=1)

    paginator = Paginator(chat_messages, per_page=15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {'profile': profile,
               'chat_receiver': chat_receiver,
               'chat_messages': reversed(page_obj),
               'chat_length': len(page_obj),
               'page_obj': page_obj,
               'chat_id': chat_id}

    if 'message_text' in request.POST:
        chat.send_message(profile, request.POST.get('message_text'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    if 'message_gift' in request.POST:
        context['gift_list'] = Gift.objects.all()

    return render(request, template_name='chat.html', context=context)


def send_chat_gift_view(request, chat_id, gift_id):
    chat = Chat.objects.get(id=chat_id)
    result = chat.send_gift(profile=request.user.user_profile, gift_id=gift_id)
    messages.add_message(request, messages.SUCCESS, result['text'])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def send_gift_view(request_profile, chat_id, gift_id):
    if request_profile:
        pass


@login_required
def delete_chat_view(request, chat_id):
    chat = Chat.objects.get(pk=chat_id)
    messages.add_message(request, messages.SUCCESS, f'Your chat {chat} was successfully deleted!')
    chat.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
# def react_like_function(request_profile, action_profile, reaction):
#     match = MatchesModel.objects.get()

class CupidPageView(LoginRequiredMixin, DataMixin, View):
    template_name = 'cupid_page.html'

    def get(self, *args, **kwargs):
        context = self.get_user_context()
        return render(self.request, template_name='cupid_page.html', context=context)

    def post(self, request):
        if 'premium-activate' in request.POST:
            premium_status = self.request.user.user_profile.pay_premium()
            messages.add_message(request, messages.WARNING, f'{premium_status["text"]}')
            return redirect('profile')



class CupidBuyPage(DataMixin, LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        context = self.get_user_context()
        return render(request, template_name='cupid_buy.html', context=context)

    def post(self, request):
        context = self.get_user_context()
        amount = request.POST.get('buy')
        cupid_buy = transaction_cupids(request_profile=context['profile'], amount=amount)
        messages.add_message(request, messages.SUCCESS, f'{cupid_buy["text"]}')
        return redirect('cupid_buy')

# def cupid_buy_page(request):
#     profile = request.user.user_profile
#
#     context = {'profile': profile
#                }
#
#     if 'buy' in request.POST:
#         print(f'{profile}', f'value {request.POST.get("buy")}')
#         amount = request.POST.get('buy')
#         result = transaction_cupids(request_profile=profile, amount=amount)
#         if result['success']:
#             messages.add_message(request, messages.SUCCESS, f'{result["text"]}')
#         else:
#             messages.add_message(request, messages.WARNING, f'{result["text"]}')
#
#     return render(request, template_name='cupid_buy.html', context=context)

# def activate_premium(request_profile: Profile):
#     request_profile.pay_premium()
#         with transaction.atomic():
#             result = transaction_cupids(request_profile, -90)
#             request_profile.vip_status = True
#             request_profile.save()
#             return {'success': True,
#                     'text': 'You are premium member now, congrats!'}
#     else:
#         return {'success': False,
#                 'text': 'You are already premium'}

def transaction_cupids(request_profile, amount):

    try:
        print('Trying transcation cupids.')
        new_balance = request_profile.cupid_transaction(amount=amount)
        return {'success': True,
                'text': f'You successfully bought {amount} cupids'}
    except:
        print('Not enough money transaction cupids 182')
        return {'success': False,
                'text': 'Not enough money'}



class ReactLikeView(DataMixin, ProfileSetupedMixin, LoginRequiredMixin, View):

    def get(self, action_user_id, reaction):
        context = self.get_context_data()
        action_user = Profile.objects.get(user_id=action_user_id)
        react_result = react_like(context['profile'], action_user, reaction)
        messages.add_message(self.request, messages.INFO, f"{react_result['text']}")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))



def ReactLikeV1iew(request, action_user_id, reaction):
    request_profile: Profile = Profile.get_profile(user_id=request.user.id)
    action_profile: Profile = Profile.get_profile(user_id=action_user_id)
    react_result = react_like(request_profile, action_profile, reaction)

    if react_result['match-status'] == 'like':
        messages.add_message(request, messages.SUCCESS, f'You matched with {action_profile}')
        new_chat = Chat(profile1=request_profile, profile2=action_profile)
        new_chat.save()

    elif react_result['match-status'] == 'dislike':
        messages.add_message(request, messages.WARNING, f'You disliked {action_profile}')
    time.sleep(1.5)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class MatchesPageView(DataMixin, ProfileSetupedMixin, LoginRequiredMixin, ListView):

    template_object_name = 'profiles'
    model = Profile
    template_name = 'matches.html'


    def get_context_data(self, *args, **kwargs):
        context = self.get_user_context()
        profile_matches = context['profile'].matches()

        matches_with_receivers = []
        for match in profile_matches:
            if match.user_liker != context['profile']:
                matches_with_receivers.append({'match': match,
                                               'profile': match.user_liker})
            else:
                matches_with_receivers.append({
                    'match': match,
                    'profile': match.user_liked
                })

        context['profiles'] = matches_with_receivers
        return context
@login_required
def Matches1PageView(request):
    """
    MatchesPageView
    Finds matches and extracts matched profile info
    """
    profile = request.user.user_profile

    profile_matches = profile.matches()

    matches_with_receivers = []

    for match in profile_matches:
        if match.user_liker != profile:
            matches_with_receivers.append({'match': match,
                          'profile': match.user_liker})
        else:
            matches_with_receivers.append({
                'match': match,
                'profile': match.user_liked
            })

    matches_profiles = []
    print(matches_with_receivers)
    context = {'profile': profile,
               'profiles': matches_with_receivers,
               'unread_messages': profile.get_unread_chats()}

    return render(request, template_name='matches.html', context=context)


class DatesPageView(DataMixin, ProfileSetupedMixin, LoginRequiredMixin, View):

    template_name = 'dates.html'

    def get(self, *args, **kwargs):
        context = self.get_user_context()
        filtered_dates_list = Profile.objects.exclude(
            user_id__in=(o['user_liked__user_id'] for o in find_all_user_liked(context['profile']))). \
            exclude(user_id__in=[o['user_liker__user_id'] for o in find_who_liked_user(context['profile'])])
        print(filtered_dates_list, 'Its last users')
        if filtered_dates_list:
            context['date_profile'] = random.choice(filtered_dates_list)
        return render(self.request, template_name='dates.html', context=context)


    def post(self, *args, **kwargs):
        context = self.get_user_context()
        if 'like' in self.request.POST:
            action = {'reaction': 'like',
                      'profile_id': self.request.POST.get('like')}
        else:
            action = {'reaction': 'dislike',
                      'profile_id': self.request.POST.get('dislike')}
        reaction = like_someone(context['profile'], action_user_id=action['profile_id'], reaction=action['reaction'])
        messages.add_message(self.request, messages.SUCCESS, f'{reaction["message"]}')
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

@login_required
def DatesPageV1iew(request):
    user_profile = request.user.user_profile

    filtered_dates_list = Profile.objects.exclude(user_id__in=[o['user__liked_user_id'] for o in find_all_user_liked(user_profile)]).\
                                                                                        exclude(user_id__in=[o['user__liked_user_id'] for o in find_who_liked_user(user_profile)])

    print(filtered_dates_list)
    context = {'profile': user_profile,
               'unread_messages': user_profile.get_unread_chats()}


    if filtered_dates_list:
        b = random.randint(0, len(filtered_dates_list)-1)
        context['date_profile'] = filtered_dates_list[b]

    if 'like' in request.POST:
        action_user_id = request.POST.get('like')
        print('ACTION USER ID IS: ', action_user_id)
        message = like_someone(user_profile, action_user_id=action_user_id, reaction='like')
        messages.add_message(request, messages.SUCCESS, message=message['message'])

    if 'dislike' in request.POST:
        action_user_id = request.POST.get('dislike')
        print('ACTION USER ID IS: ', action_user_id)
        message = like_someone(user_profile, action_user_id=action_user_id, reaction='dislike')
        messages.add_message(request, messages.SUCCESS, message=message['message'])

    return render(request, template_name='dates.html', context=context)
