from users.models import Progress
from django.urls import reverse

def get_group_features(group_name):
    """Grup adına göre sahip olduğu özellikleri döndürür"""
    if not group_name:
        return {
            'has_leaderboard': False,
            'has_progress_bar': False,
            'has_features': False,
            'is_team_based': False
        }
    
    features = {
        'A': {'has_leaderboard': True, 'has_progress_bar': False, 'has_features': True, 'is_team_based': False},
        'B': {'has_leaderboard': False, 'has_progress_bar': True, 'has_features': True, 'is_team_based': False},
        'C': {'has_leaderboard': True, 'has_progress_bar': False, 'has_features': True, 'is_team_based': True},
        'D': {'has_leaderboard': False, 'has_progress_bar': True, 'has_features': True, 'is_team_based': True},
        'E': {'has_leaderboard': False, 'has_progress_bar': False, 'has_features': False, 'is_team_based': False},
        'F': {'has_leaderboard': False, 'has_progress_bar': False, 'has_features': False, 'is_team_based': True}
    }
    
    return features.get(group_name, {
        'has_leaderboard': False,
        'has_progress_bar': False,
        'has_features': False,
        'is_team_based': False
    })
    
    
def update_user_points(user, points):
    progress, created = Progress.objects.get_or_create(user=user)
    progress.points += points
    progress.check_for_level_up()
    progress.save()
        

def get_leaderboard_url(user):
    """Kullanıcının grubuna göre doğru leaderboard URL'sini döndürür"""
    if user.group and user.group.name in ['C', 'D', 'F']:  
        return reverse('team_leaderboard')
    else:
        return reverse('group_leaderboard')
    

def get_user_ranking_info(user):
    """
    Kullanıcının grubuna göre bireysel veya takım sıralaması bilgilerini döndürür.
    
    Eğer kullanıcı takım bazlı bir gruptaysa:
    - Takım sıralaması bilgisi
    - Takımın toplam puanı
    
    Eğer kullanıcı bireysel bir gruptaysa:
    - Bireysel sıralama bilgisi
    - Bireysel puan
    """
    from users.models import Progress
    from django.db.models import Sum
    
    if not user.group:
        return {
            'is_team_based': False,
            'rank': '-',
            'points': 0,
            'total_members': 0
        }
    
    is_team_based = user.group.is_team_based
    
    if is_team_based and user.team:
        teams = user.group.teams.all()
        team_points = []
        
        for team in teams:
            points = Progress.objects.filter(user__team=team).aggregate(Sum('points'))['points__sum'] or 0
            team_points.append({'team': team, 'points': points})
        
        sorted_teams = sorted(team_points, key=lambda x: x['points'], reverse=True)
        
        user_team_rank = 0
        for i, data in enumerate(sorted_teams):
            if data['team'] == user.team:
                user_team_rank = i + 1
                break
                
        team_points = sorted_teams[user_team_rank-1]['points'] if user_team_rank > 0 else 0
        
        return {
            'is_team_based': True,
            'rank': user_team_rank,
            'points': team_points,
            'total_members': len(sorted_teams),
            'team_name': user.team.name
        }
    else:
        progress, created = Progress.objects.get_or_create(user=user)
        
        total_members = Progress.objects.filter(user__group=user.group).count()
        
        user_rank = Progress.objects.filter(user__group=user.group, points__gt=progress.points).count() + 1
        
        return {
            'is_team_based': False,
            'rank': user_rank,
            'points': progress.points,
            'total_members': total_members
        }