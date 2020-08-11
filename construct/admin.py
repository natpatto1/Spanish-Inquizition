from django.contrib import admin
from .models import Verbs, Pronouns, Article

# Register your models here.

admin.site.register(Verbs)
admin.site.register(Pronouns)
admin.site.register(Article)