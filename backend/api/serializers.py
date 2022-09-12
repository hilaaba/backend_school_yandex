from rest_framework.exceptions import ValidationError
from rest_framework.fields import DateTimeField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    CharField, ChoiceField, IntegerField, ModelSerializer, Serializer,
    SerializerMethodField, UUIDField
)

from .models import CHOICES, FILE, History, Item
from .services import get_or_none
from .validators import validate_uuid


class ItemSerializer(ModelSerializer):
    parentId = PrimaryKeyRelatedField(
        source='parent',
        queryset=Item.objects.all(),
        allow_null=True,
    )
    children = SerializerMethodField(read_only=True)
    type = ChoiceField(choices=CHOICES)

    class Meta:
        model = Item
        exclude = ('parent',)

    def validate_url(self, url):
        if url is None:
            return None
        if url[0] != '/':
            raise ValidationError('Url must start with slash')
        return url

    def validate(self, data):
        try:
            if data.get('type') == FILE:
                size = data.get('size')
                assert isinstance(size, int) and size >= 0
            else:
                assert 'size' not in data
        except AssertionError:
            raise ValidationError('Invalid size')
        return data

    def get_children(self, obj):
        if obj.type == FILE:
            return None
        return self.__class__(obj.histories.all(), many=True).data


class ItemRequest:
    def __init__(self, items, updateDate):
        self.items = updateDate
        self.items = items


class ItemImportRequestSerializer(Serializer):
    items = ListField(allow_null=True)
    updateDate = DateTimeField()

    def create(self, validated_data):
        instance = ItemRequest(**validated_data)
        items = validated_data.get('items')
        for item in items:
            uuid = validate_uuid(item.get('id'))
            unit = get_or_none(Item, pk=uuid)
            item['date'] = validated_data['updateDate']

            if unit:
                item_serializer = ItemSerializer(unit, data=item)
            else:
                item_serializer = ItemSerializer(data=item)
            if not item_serializer.is_valid():
                raise ValidationError(item_serializer.errors)
            item_serializer.save()
        return instance


class HistorySerializer(ModelSerializer):
    type = CharField(default=FILE)

    class Meta:
        model = History
        fields = '__all__'
