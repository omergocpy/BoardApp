def navbar_context(request):
    if request.user.is_authenticated:
        progress = getattr(request.user, 'progress_instance', None)
        if progress:
            level = progress.level
            points = progress.points
        else:
            level = 1
            points = 0
        is_admin = request.user.is_superuser
        return {'level': level, 'points': points, 'is_admin': is_admin}
    return {}
