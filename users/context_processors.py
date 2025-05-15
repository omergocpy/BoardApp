from users.utils import get_group_features, get_leaderboard_url, get_user_ranking_info

def navbar_context(request):
    if request.user.is_authenticated:
        progress = getattr(request.user, 'progress_instance', None)
        ranking_info = get_user_ranking_info(request.user)
        
        group_name = request.user.group.name if request.user.group else None
        
        # Grup bazlı görünüm özellikleri
        show_progress_bar = False
        show_leaderboard = False
        
        # B ve D grupları için progress bar göster
        if group_name in ['B', 'D']:
            show_progress_bar = True
            
        # A ve C grupları için leaderboard göster
        if group_name in ['A', 'C']:
            show_leaderboard = True
            
        group_features = get_group_features(group_name)
        
        # Takım bilgisi (takım bazlı gruplar için C, D, F)
        team_name = None
        if request.user.team and group_name in ['C', 'D', 'F']:
            team_name = request.user.team.name
        
        if progress:
            level = progress.level
            points = progress.points
            progress_text = progress.get_level_progress_text()
        else:
            level = 1
            points = 0
            progress_text = "Seviye 1 (0/100)"
            
        is_admin = request.user.is_superuser
        leaderboard_url = get_leaderboard_url(request.user)
        
        return {
            'level': level, 
            'points': points, 
            'progress_text': progress_text,
            'is_admin': is_admin,
            'leaderboard_url': leaderboard_url,
            'show_progress_bar': show_progress_bar,
            'show_leaderboard': show_leaderboard,
            'is_team_based': ranking_info['is_team_based'],
            'team_name': team_name,
            'group_features': group_features, 
            'group_name': None  # Grup adı kullanıcılara gösterilmeyecek
        }
    return {}