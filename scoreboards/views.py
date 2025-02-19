from django.shortcuts import render, get_object_or_404
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