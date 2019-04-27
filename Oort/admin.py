from django.contrib import admin

from .models import Content, Genre, Cast, Director

admin.site.register(Content)
admin.site.register(Genre)
admin.site.register(Cast)
admin.site.register(Director)
