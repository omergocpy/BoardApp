from django.contrib import admin
from .models import Post, Comment, Like, Rating, Category, Poll, PollOption, PollVote
from django.http import HttpResponseRedirect
import traceback
from django.db import connection, transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]

@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'user', 'option', 'created_at')
    list_filter = ('poll', 'user', 'option')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'post_type', 'created_at', 'approved', 'points_added')
    list_filter = ('approved', 'points_added', 'created_at', 'post_type')
    search_fields = ('user__username', 'content')
    actions = ['approve_posts', 'reset_approval', 'reset_points_added']
    
    def approve_posts(self, request, queryset):
        """Gönderileri onaylar - puanlar signal ile eklenecek"""
        updated_count = queryset.filter(approved=False).update(approved=True)
        
        if updated_count == 1:
            message_bit = "1 gönderi"
        else:
            message_bit = f"{updated_count} gönderi"
            
        self.message_user(request, f"{message_bit} onaylandı. Puanlar otomatik eklenecek.")
    
    approve_posts.short_description = "Seçili gönderileri onayla"
    
    def reset_approval(self, request, queryset):
        """Test için onay durumunu sıfırlar"""
        updated_count = queryset.update(approved=False)
        self.message_user(request, f"{updated_count} gönderinin onay durumu sıfırlandı.")
    
    reset_approval.short_description = "Seçili gönderilerin onayını sıfırla"
    
    def reset_points_added(self, request, queryset):
        """Test için puan eklendi durumunu sıfırlar"""
        updated_count = queryset.update(points_added=False)
        self.message_user(request, f"{updated_count} gönderinin puan eklendi durumu sıfırlandı.")
    
    reset_points_added.short_description = "Seçili gönderilerin puan durumunu sıfırla"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at', 'approved', 'points_added')
    list_filter = ('approved', 'points_added', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments', 'reset_approval', 'reset_points_added']
    
    def approve_comments(self, request, queryset):
        """Yorumları onaylar - puanlar signal ile eklenecek"""
        updated_count = queryset.filter(approved=False).update(approved=True)
        
        self.message_user(request, f"{updated_count} yorum onaylandı. Puanlar otomatik eklenecek.")
    
    approve_comments.short_description = "Seçili yorumları onayla"
    
    def reset_approval(self, request, queryset):
        """Test için onay durumunu sıfırlar"""
        updated_count = queryset.update(approved=False)
        self.message_user(request, f"{updated_count} yorumun onay durumu sıfırlandı.")
    
    reset_approval.short_description = "Seçili yorumların onayını sıfırla"
    
    def reset_points_added(self, request, queryset):
        """Test için puan eklendi durumunu sıfırlar"""
        updated_count = queryset.update(points_added=False)
        self.message_user(request, f"{updated_count} yorumun puan eklendi durumu sıfırlandı.")
    
    reset_points_added.short_description = "Seçili yorumların puan durumunu sıfırla"




@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'like_type', 'created_at', 'approved', 'points_added')
    list_filter = ('like_type', 'approved', 'points_added', 'created_at')
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['direct_points_action', 'debug_action', 'reset_approval', 'reset_points_added']
    
    def direct_points_action(self, request, queryset):
        """Beğenilere doğrudan puan ekleme (SQL yerine ORM kullanarak)"""
        updated_count = 0
        
        for like in queryset:
            try:
                # Beğeni bilgilerini al
                user_id = like.user.id
                post_owner_id = like.post.user.id
                like_type = like.like_type
                username = like.user.username
                
                # Beğeniyi onaylı yap
                like.approved = True
                like.save(update_fields=['approved'])
                
                # Kendi gönderisini beğenmiyorsa puan ekle
                if user_id != post_owner_id:
                    # Progress kaydı var mı kontrol et
                    from users.models import Progress
                    
                    # Transaction kullanarak daha güvenli hale getir
                    with transaction.atomic():
                        try:
                            progress = Progress.objects.select_for_update().get(user_id=user_id)
                            current_points = progress.points
                            
                            # Beğeni tipine göre puan ekle/çıkar
                            if like_type == 'like':
                                new_points = current_points + 10
                                point_text = "+10"
                            else:
                                new_points = current_points - 10
                                point_text = "-10"
                            
                            # Progress nesnesini güncelle
                            progress.points = new_points
                            progress.save()
                            
                            # Beğeniyi işaretleme (transaction içinde)
                            like.points_added = True
                            like.save(update_fields=['points_added'])
                            
                            updated_count += 1
                            print(f"ID {like.id}: {username} kullanıcısına {point_text} puan eklendi. {current_points} -> {new_points}")
                            
                        except Progress.DoesNotExist:
                            # Progress kaydı yoksa oluştur
                            points = 10 if like_type == 'like' else -10
                            Progress.objects.create(user_id=user_id, points=points, level=1)
                            
                            # Beğeniyi işaretle
                            like.points_added = True
                            like.save(update_fields=['points_added'])
                            
                            updated_count += 1
                            print(f"ID {like.id}: {username} için yeni progress kaydı oluşturuldu, {points} puan eklendi.")
                else:
                    # Kendi gönderisini beğenmişse sadece işaretle
                    like.points_added = True
                    like.save(update_fields=['points_added'])
                    print(f"ID {like.id}: {username} kendi gönderisini beğenmiş, puan eklenmedi.")
                
            except Exception as e:
                print(f"HATA (Beğeni ID {like.id}): {str(e)}")
                import traceback
                print(traceback.format_exc())
                self.message_user(request, f"Beğeni ID {like.id} için hata oluştu: {str(e)}", level='ERROR')
                
        self.message_user(request, f"{updated_count} beğeni için puanlar doğrudan eklendi ve işaretlendi.")
    
    direct_points_action.short_description = "Seçili beğeniler için doğrudan puan ekle"
    
    # Debug ve diğer metodları da ekleyin...
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'score', 'created_at', 'approved', 'points_added')
    list_filter = ('score', 'approved', 'points_added', 'created_at')
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['approve_ratings', 'reset_approval', 'reset_points_added']
    
    def approve_ratings(self, request, queryset):
        """Derecelendirmeleri onaylar - puanlar signal ile eklenecek"""
        updated_count = queryset.filter(approved=False).update(approved=True)
        
        if updated_count == 1:
            message_bit = "1 derecelendirme"
        else:
            message_bit = f"{updated_count} derecelendirme"
        
        self.message_user(request, f"{message_bit} onaylandı. Puanlar otomatik eklenecek.")
    
    approve_ratings.short_description = "Seçili derecelendirmelere onay ver"
    
    def reset_approval(self, request, queryset):
        """Test için onay durumunu sıfırlar"""
        updated_count = queryset.update(approved=False)
        self.message_user(request, f"{updated_count} derecelendirmenin onay durumu sıfırlandı.")
    
    reset_approval.short_description = "Seçili derecelendirmelerin onayını sıfırla"
    
    def reset_points_added(self, request, queryset):
        """Test için puan eklendi durumunu sıfırlar"""
        updated_count = queryset.update(points_added=False)
        self.message_user(request, f"{updated_count} derecelendirmenin puan eklendi durumu sıfırlandı.")
    
    reset_points_added.short_description = "Seçili derecelendirmelerin puan durumunu sıfırla"