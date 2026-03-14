from django.contrib import admin
from .models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'folder', 'timestamp', 'read')
    list_filter = ('folder', 'read', 'timestamp')
    search_fields = ('subject', 'body', 'sender__username', 'recipient__username')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('sender', 'recipient')
    readonly_fields = ('slug', 'timestamp')
    
    fieldsets = (
        (None, {
            'fields': ('sender', 'recipient', 'subject', 'body')
        }),
        ('Статус', {
            'fields': ('folder', 'read', 'slug', 'timestamp')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'move_to_trash']
    
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = 'Отметить как прочитанное'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = 'Отметить как непрочитанное'
    
    def move_to_trash(self, request, queryset):
        queryset.update(folder='trash')
    move_to_trash.short_description = 'Переместить в корзину'
