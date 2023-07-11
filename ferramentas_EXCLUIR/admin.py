from django.contrib import admin
from ferramentas_EXCLUIR.models import App

# Register your models here.
@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ['id','nome']
    search_fields = ['nome','desc']
    ordering = '-id',