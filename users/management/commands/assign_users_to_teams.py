from django.core.management.base import BaseCommand
from users.models import CustomUser, Team, Group

class Command(BaseCommand):
    help = 'Takım bazlı gruplardaki kullanıcıları takımlara atar'

    def handle(self, *args, **kwargs):
        team_based_groups = Group.objects.filter(is_team_based=True)
        
        for group in team_based_groups:
            self.stdout.write(self.style.SUCCESS(f"Grup {group.get_name_display()} işleniyor..."))
            
            teams = Team.objects.filter(group=group)
            if not teams.exists():
                self.stdout.write(self.style.ERROR(f"  - Grup {group.get_name_display()} için takım bulunamadı!"))
                continue
            
            users = CustomUser.objects.filter(group=group, team__isnull=True)
            
            if not users.exists():
                self.stdout.write(self.style.WARNING(f"  - Grup {group.get_name_display()} için atanacak kullanıcı bulunamadı!"))
                continue
            
            self.stdout.write(self.style.SUCCESS(f"  - {users.count()} kullanıcı atanacak"))
            
            teams_list = list(teams)
            
            for i, user in enumerate(users):
                team = teams_list[i % len(teams_list)]
                
                user.team = team
                user.save()
                
                self.stdout.write(f"  - {user.username} -> {team.name}")
            
        self.stdout.write(self.style.SUCCESS("Kullanıcıları takımlara atama işlemi tamamlandı."))