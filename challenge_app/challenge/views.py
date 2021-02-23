from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Max
from django.shortcuts import render
from challenge.models import JoinCode, Player
from challenge.forms import JoinForm, RegisterForm
from challenge.forms import ChallengeForm
from challenge.models import Match
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd


# Create your views here.
@login_required
def home(request):
    current_group = request.user.player.active_group

    if current_group:
        # players = Player.objects.filter(user__groups=current_group)
        # # for p in players:
        # #     p.score = p.current_score(current_group)
        # # players.order_by('score')
        return render(request, 'challenge/dashboard.html',
                      {
                          'matches': Match.objects.exclude(played_at=None).filter(
                              group=request.user.player.active_group, cancelled_at=None),
                          'planned': Match.objects.filter(played_at=None, cancelled_at=None,
                                                          group=request.user.player.active_group),
                      })
    else:
        return render(request, 'challenge/group_not_found.html')


@login_required
def challenge(request):
    if not request.user.player.active_group:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        group = Group.objects.get(id=request.user.player.active_group.id)
        opponents = User.objects.filter(groups=group.id).exclude(id=request.user.id)
        return render(request, 'challenge/create_match.html',
                      {
                          'opponents': opponents
                      })
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            opponent = User.objects.get(id=form.cleaned_data['opponent']).player
            group = request.user.player.active_group
            match = Match(challenger=request.user.player, opponent=opponent, date=form.cleaned_data['datetime'],
                          group=group)
            match.save()
            return HttpResponseRedirect("/") # "/match/{id}".format(id=match.id)
        else:
            return HttpResponseRedirect('/challenge')


@login_required
def match(request, match_id):
    match = Match.objects.get(id=match_id)
    if match is not None:
        return render(request, 'challenge/match.html', {'match': match, 'ch_score': match.challenger.current_score(group=match.group), 'op_score': match.opponent.current_score(group=match.group)})
    return render(request, 'challenge/error.html', {'error': {'message': "Match not found..."}})

@login_required
def submit_match(request, match_id):
    match = Match.objects.get(id=match_id)
    if match is not None:
        if request.user not in [match.challenger.user, match.opponent.user]:
            return render(request, 'challenge/error.html', {'error': { "Dat mag dus niet..." }})
        if match.played_at is not None:
            return render(request, 'challenge/error.html', { 'error': {'message': "Match already submitted"}})
        if request.method == 'GET':
            return render(request, 'challenge/match_submit.html', { 'match': match })
        if request.method == 'POST':
            match.submit_result(challenger_wins=(request.POST['winner'] == 'challenger'))
            return HttpResponseRedirect('/')

def join(request):
    if request.method == 'GET':
        try:
            code = JoinCode.objects.get(key=request.GET['code'])
        except:
            return HttpResponse("Not a valid invite code")
        else:
            if request.user.is_authenticated:
                request.user.groups.add(code.group_id)
                return HttpResponseRedirect('/')
            return render(request, 'registration/join_group.html')
    if request.method == 'POST':
        form = JoinForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                return HttpResponseRedirect(
                    '/login?code=' + request.POST['code'] + '&email=' + form.cleaned_data['email'])
            else:
                return HttpResponseRedirect('/register?code=' + request.POST['code'] + '&email=' + form.cleaned_data['email'])


@login_required
def score(request):
    current_group = request.user.player.active_group
    players = Player.objects.filter(user__groups=current_group)
    df = pd.DataFrame({
        'player': map(lambda s: s.user.username, players),
        'score': map(lambda s: s.current_score(current_group), players)
    })
    df.sort_values('score', inplace=True)
    return HttpResponse(df.to_json(), content_type='application/json')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, 'registration/register.html', {'error_email': form.cleaned_data['email'] + " is already in use..."})
            if form.cleaned_data['password'] != form.cleaned_data['repeat_password']:
                return render(request, 'registration/register.html', {'error_password': "Doe even je best. Wachtwoorden zijn ongelijk..."})
            user = User.objects.create_user(form.cleaned_data['display_name'], form.cleaned_data['email'], form.cleaned_data['password'])
            if 'code' in request.GET:
                code = JoinCode.objects.get(key=request.GET['code'])
                if code is not None:
                    user.groups.add(code.group)
            return HttpResponseRedirect("/login?email=" + form.cleaned_data['email'])
        else:
            return render(request, 'registration/register.html',
                          {'error_email': "Dikke schijt, er gaat een hele boel fout."})
    return render(request, 'registration/register.html', {'error_email': "Hmmmmmmm"})


@login_required
def logout(request):
    logout(request)
    return HttpResponseRedirect('/login')
