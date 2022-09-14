from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from items.models import FILE, Item
from .serializers import (
    HistorySerializer, ItemRequestImportSerializer, ItemSerializer
)
from .services import (
    RESPONSE_ITEM_NOT_FOUND, RESPONSE_OK, RESPONSE_VALIDATION_ERROR,
    get_date_range, get_datetime_object, get_uuid,
    save_updated_items_in_history, update_folders_date, update_sizes
)


class ItemAPIView(APIView):
    def get(self, request, uuid):
        try:
            uuid = get_uuid(uuid)
        except ValidationError:
            return RESPONSE_VALIDATION_ERROR
        try:
            item = Item.objects.get(pk=uuid)
        except Item.DoesNotExist:
            return RESPONSE_ITEM_NOT_FOUND
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, uuid):
        try:
            uuid = get_uuid(uuid)
        except ValidationError:
            return RESPONSE_VALIDATION_ERROR
        try:
            item = Item.objects.get(pk=uuid)
        except Item.DoesNotExist:
            return RESPONSE_ITEM_NOT_FOUND
        item.delete()
        return RESPONSE_OK

    def post(self, request):
        serializer = ItemRequestImportSerializer(data=request.data)
        if not serializer.is_valid():
            return RESPONSE_VALIDATION_ERROR
        try:
            serializer.save()
        except (ValidationError, Exception):
            return RESPONSE_VALIDATION_ERROR
        update_date = serializer.validated_data.get('updateDate')
        items = serializer.validated_data.get('items')
        update_folders_date(items, update_date)
        update_sizes()
        save_updated_items_in_history(update_date)
        return RESPONSE_OK


@api_view(['GET'])
def get_updates(request):
    try:
        date = get_datetime_object(request.GET.get('date'))
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    date_range = get_date_range(date)
    queryset = Item.objects.filter(date__range=date_range).filter(type=FILE)
    serializer = ItemSerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTP_200_OK)


@api_view(['GET'])
def get_history(request, uuid):
    try:
        uuid = get_uuid(uuid)
        date_start = get_datetime_object(request.GET.get('dateStart'))
        date_end = get_datetime_object(request.GET.get('dateEnd'))
    except (ValidationError, Exception):
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
