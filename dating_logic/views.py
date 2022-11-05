from django.shortcuts import render, redirect
from accounts.models import Profile
from .models import MatchesModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse


def HomePageView(request):
    if request.user.is_authenticated:
        return redirect('gallery')
    else:
        return redirect('login')

@login_required
def LikeView(request, user2, reaction):
    """
    LikeView
    Firstly checks if other-side-user had liked request user before if had - makes match
    and redirects to other-side-user profile.
    If not creates match record in database with like from one side.
    """
    profile = Profile.get_profile(request.user.id)
    profile2 = Profile.get_profile(user2)
    print(profile, profile2)
    match = None

    try:
        match = MatchesModel.objects.filter(Q(user_liker=profile2, user_liked=profile) |Q(user_liker=profile, user_liked=profile2))[:1].get()
        print('Match exist')
    except:
        print('Not exist')
    if match:
        if reaction == 'like':
            if match.user_liker != profile:
                match.like(who_likes='liked')
                messages.add_message(request, messages.SUCCESS,
                                     f'Its a match with {profile2.first_name} {profile2.last_name}!')
            else:
                messages.add_message(request, messages.WARNING, 'You cant like one profile twice!')
        elif reaction == 'dislike':
            match.dislike(who_dislikes='liked')
            match.status = 2
            messages.add_message(request, messages.INFO, f'You disliked {profile2.first_name} {profile2.last_name}')
        return HttpResponse(status=200)
    else:
        match = MatchesModel(user_liker=profile, user_liked=profile2)
        if reaction == 'like':
            match.like(who_likes='liker')
            messages.add_message(request, messages.INFO, f'You liked {profile2.first_name} {profile2.last_name}')
        elif reaction == 'dislike':
            match.dislike(who_dislikes='liker')
            match.save()
            messages.add_message(request, messages.INFO, f'You disliked {profile2.first_name} {profile2.last_name}')
        return HttpResponse(status=200)

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

    filtered_matches_list = MatchesModel.objects.filter(~Q(status=2), ~Q(user_liked=user_profile))

    user_likes_list = []
    for i in filtered_matches_list:
        print('I ===: ', i)
        user_likes_list.append(i.user_liker)

    profiles = Profile.objects.filter(~Q(gender=user_profile.gender)).exclude(user_id=request.user.id)


    print('PROFILES:', profiles,
          'FILTERED', filtered_matches_list)
    context = {'profile': user_profile}
    if request.POST:
        for _ in profiles:
            if _ not in user_likes_list:
                context['profiles'] = _
                if 'like' in request.POST:
                    return redirect('like', user2=_.user_id, reaction='like')
                elif 'dislike' in request.POST:
                    return redirect('like', user2=_.user_id, reaction='dislike')
        # if 'like' in request.POST:
        #     print(i)
        #     context['profile'] = i

    return render(request, template_name='dates.html', context=context)
# Create your views here.
