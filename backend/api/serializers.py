from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField, ChoiceField,
    Serializer, CharField, UUIDField, IntegerField
)
from .models import Item, History, CHOICES


class ItemSerializer(ModelSerializer):
    parentId = PrimaryKeyRelatedField(
        source='parent',
        queryset=Item.objects.all(),
        allow_null=True,
    )
    children = SerializerMethodField()
    type = ChoiceField(choices=CHOICES)

    class Meta:
        model = Item
        fields = (
            'id',
            'type',
            'url',
            'parentId',
            'children',
            'date',
            'size',
        )

    def get_children(self, obj):
        if obj.type == 'FILE':
            return None
        return self.__class__(obj.item_set.all(), many=True).data


class HistorySerializer(ModelSerializer):
    type = CharField(default='FILE')

    class Meta:
        model = History
        fields = '__all__'
