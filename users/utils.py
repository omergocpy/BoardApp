from users.models import Progress

def update_user_points(user, points):
    print(f"{user.username} kullanıcısına {points} puan ekleniyor.")

    progress, created = Progress.objects.get_or_create(user=user)

    progress.points += points
    progress.check_for_level_up()
    progress.save()

    # Veritabanında güncellenen puanı kontrol et
    print(f"Güncel puan: {progress.points}")
