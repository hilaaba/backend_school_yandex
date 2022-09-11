import json

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .models import Item
from .serializers import ItemSerializer, HistorySerializer
from .services import (
    create_item_instance, get_date_range,
    get_datetime_object,
    get_update_data, save_history, update_dates,
    update_sizes,
)
from .validators import validate_all_params, validate_date, validate_uuid


class ItemAPIView(APIView):
    def get(self, request, uuid):
        try:
            validate_uuid(uuid)
        except ValidationError as e:
            return Response(
                {'code': HTTP_400_BAD_REQUEST, 'message': e.message},
                status=HTTP_400_BAD_REQUEST,
            )
        item = get_object_or_404(Item, pk=uuid)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, uuid):
        try:
            validate_uuid(uuid)
        except ValidationError as e:
            return Response(
                {'code': HTTP_400_BAD_REQUEST, 'message': e.message},
                status=HTTP_400_BAD_REQUEST,
            )
        item = get_object_or_404(Item, pk=uuid)
        item.delete()
        return Response({'code': HTTP_200_OK, 'message': 'Deleted'})


@api_view(['POST'])
@transaction.atomic
def import_items(request):
    request_body = json.loads(request.body.decode())
    update_date = request_body['updateDate']
    items = request_body['items']

    affected_folders_ids, updated_or_added_ids = get_update_data(items)

    for item in items:
        try:
            validate_all_params(item, update_date)
            item_instance = create_item_instance(item, update_date)
        except ValidationError as e:
            transaction.set_rollback(True)
            return Response(
                {'code': HTTP_400_BAD_REQUEST, 'message': e.message},
                status=HTTP_400_BAD_REQUEST,
            )
        item_instance.save()

    update_dates(affected_folders_ids, update_date)
    update_sizes()
    for item_id in updated_or_added_ids:
        save_history(item_id)
    return Response(
        {'code': HTTP_200_OK, 'message': "Import or update went successful"},
    )


@api_view(['GET'])
def get_updates(request):
    request_date = request.GET.get('date')
    try:
        validate_date(request_date)
    except ValidationError as e:
        return Response(
            {'code': HTTP_400_BAD_REQUEST, 'message': e.message},
            status=HTTP_400_BAD_REQUEST,
        )
    date_range = get_date_range(request_date)
    serializer = ItemSerializer(
        Item.objects.filter(date__range=date_range).filter(type='FILE'),
        many=True,
    )
    return Response({'items': serializer.data})


@api_view(['GET'])
def get_history(request, uuid):
    date_start = request.GET.get('dateStart')
    date_end = request.GET.get('dateEnd')
    try:
        validate_uuid(uuid)
        validate_date(date_start)
        validate_date(date_end)
    except ValidationError as e:
        return Response(
            {'code': HTTP_400_BAD_REQUEST, 'message': e.message},
            status=HTTP_400_BAD_REQUEST,
        )

    item = get_object_or_404(Item, pk=uuid)
    date_start = get_datetime_object(date_start)
    date_end = get_datetime_object(date_end)

    serializer = HistorySerializer(
        item.history_set.all().filter(date__range=(date_start, date_end)),
        many=True,
    )
    return Response({'items': serializer.data})
