import time

from accounts.models import *
from dating_logic.models import MatchesModel, Chat


def find_match_between_profiles(profile1: Profile, profile2: Profile) -> MatchesModel:
    match = None
    try:
        match = MatchesModel.objects.filter(user_liked=profile1, user_liker=profile2).get()
        if match is None:
            match = MatchesModel.objects.filter(user_like=profile2, user_liker=profile1).get()
    except:
        match = MatchesModel(user_liker=profile1, user_liked=profile2, )

    return match


def find_all_user_liked(profile: Profile) -> list[Profile]:
    likes_queryset = MatchesModel.objects.filter(user_liker=profile)

    profiles_liked_list = []
    for like in likes_queryset:
        profiles_liked_list.append(like.user_liked)
    print('liked profiles',profiles_liked_list)
    return profiles_liked_list


def find_who_liked_user(profile: Profile) -> list[Profile]:
    """
    find_who_liked_user
    Function returns list of profiles who liked user with match status 0
    """
    likes_queryset = MatchesModel.objects.filter(Q(user_liked=profile) & Q(status=0))

    who_liked_list = []
    for like in likes_queryset:
        # if like.status == 0:
        who_liked_list.append(like.user_liker)
    return who_liked_list


def first_like_or_dislike(profile1, profile2: Profile, reaction: str):
    if reaction == 'like':
        like = MatchesModel(user_liker=profile1, user_liked=profile2, user_liker_like=True)
        like.save()
        return {'success': True,
                'match': like}

    elif reaction == 'dislike':
        dislike = MatchesModel(user_liker=profile1, user_liked=profile2, user_liker_like=False, status=2)
        dislike.save()
        return {'success': True,
                'match': dislike}


def react_like(profile1, profile2: Profile, reaction):
    match = find_match_between_profiles(profile1, profile2)
    if reaction == 'like':
        match.status = 1
        match.enable_chat()
        match.save()
        return {'match-status': 'match'}
    elif reaction == 'dislike':
        match.status = 2
        match.save()
        return {'match-status': 'not match'}


def like_someone(request_profile: Profile, action_user_id: int, reaction: str):
    action_profile: Profile = Profile.get_profile(user_id=action_user_id)
    already_liked_list = find_all_user_liked(request_profile)
    if action_profile not in already_liked_list:
        first_like_or_dislike(request_profile, action_profile, reaction)
    time.sleep(1.5)
    return {'success': True,
            'message': f'You successfully {reaction}d {action_profile}'}
