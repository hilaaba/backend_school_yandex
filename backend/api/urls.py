from django.urls import path

from .views import ItemAPIView, get_history, get_updates

app_name = 'api'

urlpatterns = [
    path('imports', ItemAPIView.as_view(), name='import_items'),
    path('delete/<slug:uuid>', ItemAPIView.as_view(), name='delete_item'),
    path('nodes/<slug:uuid>', ItemAPIView.as_view(), name='get_item'),
    path('updates', get_updates, name='get_updates'),
    path('node/<slug:uuid>/history', get_history, name='get_history'),
]
