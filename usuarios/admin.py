from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'empresa', 'tipo_usuario', 'created_at']
    list_filter = ['tipo_usuario', 'empresa']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
