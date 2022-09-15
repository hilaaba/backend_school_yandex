from django.core.exceptions import ValidationError
from items.models import FILE, Item
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .serializers import (
    HistorySerializer, ItemRequestImportSerializer, ItemSerializer
)
from .services import (
    RESPONSE_ITEM_NOT_FOUND, RESPONSE_OK, RESPONSE_VALIDATION_ERROR,
    get_date_range, get_datetime_object, get_uuid,
    save_updated_items_in_history, update_folders_date, update_sizes
)
from .validators import validate_date, validate_uuid


@api_view(['GET'])
def get_item(request, uuid):
    try:
        validate_uuid(uuid)
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    try:
        item = Item.objects.get(pk=uuid)
    except Item.DoesNotExist:
        return RESPONSE_ITEM_NOT_FOUND
    serializer = ItemSerializer(item)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['DELETE'])
def delete_item(request, uuid):
    try:
        validate_uuid(uuid)
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    try:
        item = Item.objects.get(pk=uuid)
    except Item.DoesNotExist:
        return RESPONSE_ITEM_NOT_FOUND
    item.delete()
    return RESPONSE_OK


@api_view(['POST'])
def import_items(request):
    serializer = ItemRequestImportSerializer(data=request.data)
    if not serializer.is_valid():
        return RESPONSE_VALIDATION_ERROR
    try:
        serializer.save()
    except Exception:
        return RESPONSE_VALIDATION_ERROR
    update_date = serializer.validated_data.get('updateDate')
    items = serializer.validated_data.get('items')
    update_folders_date(items, update_date)
    update_sizes()
    save_updated_items_in_history(update_date)
    return RESPONSE_OK


@api_view(['GET'])
def get_updates(request):
    date = request.GET.get('date')
    try:
        validate_date(date)
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    date_range = get_date_range(date)
    queryset = Item.objects.filter(date__range=date_range).filter(type=FILE)
    serializer = ItemSerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTP_200_OK)


@api_view(['GET'])
def get_history(request, uuid):
    date_start = request.GET.get('dateStart')
    date_end = request.GET.get('dateEnd')
    try:
        validate_uuid(uuid)
        validate_date(request.GET.get('dateStart'))
        validate_date(request.GET.get('dateEnd'))
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    try:
        item = Item.objects.get(pk=uuid)
    except Item.DoesNotExist:
        return RESPONSE_ITEM_NOT_FOUND
    queryset = item.history.all().filter(
        date__range=(date_start, date_end)
    )
    serializer = HistorySerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTP_200_OK)
