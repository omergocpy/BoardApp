# users/management/commands/create_teams.py

from django.core.management.base import BaseCommand
from users.models import Group, Team

class Command(BaseCommand):
    help = 'Takım bazlı gruplar için takımlar oluşturur'

    def handle(self, *args, **kwargs):
        team_names = [
            'Kaplanlar', 'Aslanlar', 'Kartallar', 'Şahinler', 'Yunuslar',
            'Fırtına', 'Yıldırım', 'Bora', 'Kasırga', 'Tayfun',
            'Alevler', 'Ateş', 'Güneş', 'Yıldız', 'Volkan'
        ]
        
        team_based_groups = ['C', 'D', 'F']
        
        for group_name in team_based_groups:
            try:
                group = Group.objects.get(name=group_name)
                
                group.is_team_based = True
                group.save()
                
                self.stdout.write(self.style.SUCCESS(f"Grup {group.get_name_display()} işleniyor..."))
                
                for i in range(5):
                    team_index = i + (team_based_groups.index(group_name) * 5)
                    team_name = team_names[team_index]
                    
                    team, created = Team.objects.get_or_create(
                        name=team_name,
                        group=group,
                        defaults={'description': f"{team_name} takımı, {group.get_name_display()} grubuna aittir."}
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"  - {team_name} takımı oluşturuldu"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  - {team_name} takımı zaten mevcut"))
                        
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Grup {group_name} bulunamadı!"))
                continue
        
        self.stdout.write(self.style.SUCCESS("Takım oluşturma işlemi tamamlandı."))