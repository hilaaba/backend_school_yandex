from django.urls import path

from .views import (
    delete_item, get_history, get_item, get_updates, import_items
)

app_name = 'api'

urlpatterns = [
    path('imports', import_items, name='import_items'),
    path('delete/<slug:uuid>', delete_item, name='delete_item'),
    path('nodes/<slug:uuid>', get_item, name='get_item'),
    path('updates', get_updates, name='get_updates'),
    path('node/<slug:uuid>/history', get_history, name='get_history'),
]
