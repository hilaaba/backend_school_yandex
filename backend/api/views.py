from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from .models import Item, FILE
from .serializers import (
    HistorySerializer, ItemRequestImportSerializer, ItemSerializer
)
from .services import (
    get_date_range, get_datetime_object, update_sizes,
    RESPONSE_VALIDATION_ERROR, RESPONSE_ITEM_NOT_FOUND,
    RESPONSE_OK, get_update_data, update_dates,
)
from .validators import validate_date, validate_uuid


class ItemAPIView(APIView):
    def get(self, request, uuid):
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

    @transaction.atomic
    def delete(self, request, uuid):
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

    def post(self, request):
        serializer = ItemRequestImportSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
             return RESPONSE_VALIDATION_ERROR
        serializer.save()
        update_date = request.data.get('updateDate')
        items = request.data.get('items')
        affected_categories_ids, updated_or_added_ids = get_update_data(items)
        update_dates(affected_categories_ids, update_date)
        update_sizes()
        for item_id in updated_or_added_ids:
            save_history(item_id)
        return RESPONSE_OK


@api_view(['GET'])
def get_updates(request):
    request_date = request.GET.get('date')
    try:
        validate_date(request_date)
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    date_range = get_date_range(request_date)
    queryset = Item.objects.filter(date__range=date_range).filter(type=FILE)
    serializer = ItemSerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTP_200_OK)


@api_view(['GET'])
def get_history(request, uuid):
    date_start = request.GET.get('dateStart')
    date_end = request.GET.get('dateEnd')
    try:
        validate_uuid(uuid)
        validate_date(date_start)
        validate_date(date_end)
    except ValidationError:
        return RESPONSE_VALIDATION_ERROR
    try:
        item = Item.objects.get(pk=uuid)
    except Item.DoesNotExist:
        return RESPONSE_ITEM_NOT_FOUND
    date_start = get_datetime_object(date_start)
    date_end = get_datetime_object(date_end)

    queryset = item.history.all().filter(
        date__range=(date_start, date_end)
    )
    serializer = HistorySerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTP_200_OK)
