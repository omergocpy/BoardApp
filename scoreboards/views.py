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
    
    if not group.is_team_based():
        return redirect('group_leaderboard')
    
    team_leaderboard = group.get_teams_leaderboard()
    
    user_team = user.team
    
    user_team_rank = next((item['rank'] for item in team_leaderboard if item['team'] == user_team), None)
    
    return render(request, 'team_leaderboard.html', {
        'team_leaderboard': team_leaderboard,
        'user_team': user_team,
        'user_team_rank': user_team_rank,
        'group': group
    })