from django.shortcuts import render, get_object_or_404,redirect
from .models import Competition, Scoreboard
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')  
def scoreboard_view(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    scoreboard_entries = Scoreboard.objects.filter(competition=competition).order_by('rank')
    return render(request, 'scoreboard.html', {
        'scoreboard_entries': scoreboard_entries,
        'competition': competition
    })
    

@login_required(login_url='login')
def team_leaderboard_view(request):
    user = request.user
    group = user.group
    
    # Eğer kullanıcı takım bazlı bir grupta değilse normal leaderboard'a yönlendir
    if not group or not group.is_team_based():
        return redirect('group_leaderboard')
    
    # Grup için takım sıralaması al
    team_leaderboard = group.get_teams_leaderboard()
    
    # Kullanıcının takımını bul
    user_team = user.team
    
    # Kullanıcının takımının sıralamasını bul
    user_team_rank = None
    if user_team:
        for item in team_leaderboard:
            if item['team'] == user_team:
                user_team_rank = item['rank']
                break
    
    return render(request, 'team_leaderboard.html', {
        'team_leaderboard': team_leaderboard,
        'user_team': user_team,
        'user_team_rank': user_team_rank,
        'group': group
    })