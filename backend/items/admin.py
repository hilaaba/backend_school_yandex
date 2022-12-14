from django.contrib import admin

from .models import History, Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'url', 'size', 'parent', 'date')


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('item', 'url', 'size', 'parent_id', 'date')


admin.site.register(Item, ItemAdmin)
admin.site.register(History, HistoryAdmin)
