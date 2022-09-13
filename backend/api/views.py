from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .models import Item
from .serializers import (
    HistorySerializer, ItemRequestImportSerializer, ItemGetSerializer
)
from .services import (
    get_date_range, get_datetime_object, get_update_data, save_history,
    update_dates, update_sizes
)
from .validators import validate_date, validate_uuid


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
        serializer = ItemGetSerializer(item)
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

    def post(self, request):
        serializer = ItemRequestImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        update_date = request.data.get('updateDate')
        items = request.data.get('items')
        affected_folders_ids, updated_or_added_ids = get_update_data(items)

        # update_dates(affected_folders_ids, update_date)
        update_sizes()
        for item_id in updated_or_added_ids:
            save_history(item_id)
        return Response(
            {
                'code': HTTP_200_OK,
                'message': "Import or update went successful"
            },
            status=HTTP_200_OK,
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
    queryset = Item.objects.filter(date__range=date_range).filter(type='FILE')
    serializer = ItemGetSerializer(queryset, many=True)
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

    queryset = item.histories.all().filter(
        date__range=(date_start, date_end)
    )
    serializer = HistorySerializer(queryset, many=True)
    return Response({'items': serializer.data})
