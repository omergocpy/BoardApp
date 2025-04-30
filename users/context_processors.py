from users.utils import get_group_features, get_leaderboard_url, get_user_ranking_info

def navbar_context(request):
    if request.user.is_authenticated:
        progress = getattr(request.user, 'progress_instance', None)
        ranking_info = get_user_ranking_info(request.user)
        
        group_name = request.user.group.name if request.user.group else None
        
        group_features = get_group_features(group_name)
        
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
            'is_team_based': ranking_info['is_team_based'],
            'team_name': ranking_info.get('team_name', ''),
            'group_features': group_features, 
            'group_name': group_name           
        }
    return {}