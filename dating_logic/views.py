import random
import time

from django.shortcuts import render, redirect
from accounts.models import Profile, CustomUserModel
from .models import MatchesModel, Chat, Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction



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


@login_required
def WhoLikedView(request):
    profile = Profile.get_profile(user_id=request.user.id)
    # who_liked_list = find_who_liked_user(profile=profile)
    matches_list = MatchesModel.objects.filter(Q(user_liked=profile) & Q(status=0))

    context = {'profile': profile,
               'likes': matches_list}

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

@login_required
def MessangerView(request):


    profile = Profile.get_profile(user_id=request.user.id)
    chats = Chat.get_user_chats(profile=profile)



    chats_with_profile_dict = []

    for chat in chats:
        chats_with_profile_dict.append({'chat':chat,
                                                 'chat_profile': chat.chat_profile(profile)})

    context = {'profile': profile,
               'chats': chats_with_profile_dict}

    if 'chat_id' in request.POST:
        chat_id = request.POST.get('chat_id')
        chat = Chat.objects.get(id=chat_id)
        selected_chat_messages = chat.get_chat_messages()
        chat_receiver = chat.get_chat_receiver(profile)
        return redirect('chat', chat_id=int(chat_id))
        context['selected_chat_messages'] = {'messages':reversed(selected_chat_messages),
                                             'chat_id': chat_id}
        context['chat_receiver'] = chat_receiver

    if 'message_text' in request.POST:
        chat_id = request.POST.get('chat_id')
        print(chat_id)
        chat = Chat.objects.get(id=chat_id)

        chat.send_message(profile=profile, message_text=request.POST.get('message_text'))



    return render(request, template_name='messanger.html', context=context)


@login_required
def ChatView(request, chat_id):

    profile = request.user.user_profile
    chat = Chat.objects.get(id=chat_id)
    chat_receiver = chat.get_chat_receiver(profile)
    chat_messages = chat.get_chat_messages()

    paginator = Paginator(chat_messages, per_page=15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'profile': profile,
               'chat_receiver': chat_receiver,
               'chat_messages': reversed(page_obj),
               'chat_length': len(page_obj),
               'page_obj': page_obj}

    if 'message_text' in request.POST:
        chat.send_message(profile, request.POST.get('message_text'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    return render(request, template_name='chat.html', context=context)


# def react_like_function(request_profile, action_profile, reaction):
#     match = MatchesModel.objects.get()

def cupid_page(request):
    profile = request.user.user_profile

    context = {'profile': profile,}

    if 'premium-activate' in request.POST:
        result = activate_premium(profile)
        messages.add_message(request, messages.WARNING, f'{result["text"]}')

    return render(request, template_name='cupid_page.html', context=context)

def cupid_buy_page(request):
    profile = request.user.user_profile

    context = {'profile': profile
               }

    if 'buy' in request.POST:
        print(f'{profile}', f'value {request.POST.get("buy")}')
        amount = request.POST.get('buy')
        result = transaction_cupids(request_profile=profile, amount=amount)
        if result['success']:
            messages.add_message(request, messages.SUCCESS, f'{result["text"]}')
        else:
            messages.add_message(request, messages.WARNING, f'{result["text"]}')

    return render(request, template_name='cupid_buy.html', context=context)

def activate_premium(request_profile: Profile):
    if request_profile.vip_status is False:
        if request_profile.cupid_balance >= 90:
            with transaction.atomic():
                result = transaction_cupids(request_profile, -90)
                request_profile.vip_status = True
                request_profile.save()
                return {'success': True,
                        'text': 'You are premium member now, congrats!'}
        else:
            return {'success': False,
                    'text': 'Not enough cupids'}
    else:
        return {'success': False,
                'text': 'You are already premium'}

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



def ReactLikeView(request, action_user_id, reaction):
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

@login_required
def MatchesPageView(request):
    """
    MatchesPageView
    Finds matches and extracts matched profile info
    """
    profile = request.user.user_profile

    profile_matches = profile.matches(MatchesModel.objects)

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
               'profiles': matches_with_receivers}

    return render(request, template_name='matches.html', context=context)


@login_required
def DatesPageView(request):
    user_profile = request.user.user_profile

    filtered_dates_list = Profile.objects.exclude(user_id__in=[o.user_id for o in find_all_user_liked(user_profile)]).\
                                                                                        exclude(user_id__in=[o.user_id for o in find_who_liked_user(user_profile)])

    print(filtered_dates_list)
    context = {'profile': user_profile}


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
