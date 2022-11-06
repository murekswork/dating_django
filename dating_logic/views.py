from django.shortcuts import render, redirect
from accounts.models import Profile
from .models import MatchesModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect

from services.business_logic import find_match_between_profiles, \
                                    find_all_user_liked, \
                                    first_like_or_dislike, \
                                    find_who_liked_user, react_like


def HomePageView(request):
    if request.user.is_authenticated:
        return redirect('gallery')
    else:
        return redirect('login')


@login_required
def LikeView(request, action_user_id, reaction):
    request_profile: Profile = Profile.get_profile(user_id=request.user.id)
    action_profile: Profile = Profile.get_profile(user_id=action_user_id)

    already_liked_list = find_all_user_liked(request_profile)

    if action_profile not in already_liked_list:
        first_like_or_dislike(request_profile, action_profile, reaction)
        messages.add_message(request, messages.INFO, f'You successfully {reaction} {action_profile}')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def WhoLikedView(request):
    profile = Profile.get_profile(user_id=request.user.id)
    who_liked_list = find_who_liked_user(profile=profile)
    print(who_liked_list)

    context = {'profile': profile,
               'likes': who_liked_list}
    return render(request, template_name='profile_likes.html', context=context)

@login_required
def ReactLikeView(request, action_user_id, reaction):
    request_profile: Profile = Profile.get_profile(user_id=request.user.id)
    action_profile: Profile = Profile.get_profile(user_id=action_user_id)
    react_result = react_like(request_profile, action_profile, reaction)
    if react_result['match-status'] == 'match':
        messages.add_message(request, messages.SUCCESS, f'You matched with {action_profile}')

    elif react_result['match-status'] == 'not match':
        messages.add_message(request, messages.WARNING, f'You disliked {action_profile}')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def MatchesPageView(request):
    """
    MatchesPageView
    Finds matches and extracts matched profile info
    """
    profile = request.user.get_profile()
    print(profile)
    user_matches_list = MatchesModel.objects.filter(status=1)
    user_matches_list = user_matches_list.filter(Q(user_liker=profile) | Q(user_liked=profile))
    print(user_matches_list)
    matches_profiles = []
    for match in user_matches_list:
        if match.user_liker != profile:
            matches_profiles.append(match.user_liker)
        else:
            matches_profiles.append(match.user_liked)

    context = {'profile': profile,
               'profiles': matches_profiles}
    return render(request, template_name='matches.html', context=context)


@login_required
def DatesPageView(request):
    user_profile = request.user.get_profile()

    filtered_dates_list = Profile.objects.exclude(user_id__in=[o.user_id for o in find_all_user_liked(user_profile)]).\
                                                                                        exclude(user_id__in=[o.user_id for o in find_who_liked_user(user_profile)])

    print(filtered_dates_list)
    context = {'profile': user_profile,}

    if filtered_dates_list:
        context['date_profile'] = filtered_dates_list[0]

    return render(request, template_name='dates.html', context=context)
