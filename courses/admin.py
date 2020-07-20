from django.contrib import admin
from .models import Levels, Spanish, PlayerScore, PlayerStatus, UserSessions
# Register your models here.


admin.site.register(Levels)
admin.site.register(Spanish)
admin.site.register(PlayerScore)
admin.site.register(PlayerStatus)
admin.site.register(UserSessions)