import json

from django.urls import reverse
from items.models import History, Item
from rest_framework.serializers import DateTimeField
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
)
from rest_framework.test import APITestCase

from .unit_test import EXPECTED_TREE, IMPORT_BATCHES, deep_sort_children

RESPONSE_VALIDATION_ERROR = {
    'code': HTTP_400_BAD_REQUEST,
    'message': 'Validation Failed',
}


RESPONSE_ITEM_NOT_FOUND = {
    'code': HTTP_404_NOT_FOUND,
    'message': 'Item not found',
}


class ItemImportTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('api:import_items')
        self.parent_data = {
            'items': [
                {
                    'type': 'FOLDER',
                    'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                    'parentId': None,
                },
            ],
            'updateDate': '2022-02-01T12:00:00Z',
        }
        self.children_data = {
            'items': [
                {
                    'type': 'FILE',
                    'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                    'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                    'size': 256,
                    'url': '/url/1',
                },
            ],
            'updateDate': '2022-02-02T12:00:00Z',
        }

    def test_import(self):
        for batch in IMPORT_BATCHES:
            with self.subTest(data=batch):
                response = self.client.post(
                    self.url,
                    data=batch,
                    format='json',
                )
                self.assertEqual(response.status_code, HTTP_200_OK)
                self.assertEqual(response.data, None)

    def test_invalid_id(self):
        self.invalid_id = '123'
        self.parent_data['items'][0]['id'] = self.invalid_id
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_duplicate_id_in_one_request(self):
        self.item_duplicate_id = {
            "type": "FOLDER",
            "id": self.parent_data['items'][0]['id'],
            "parentId": None,
        }
        self.parent_data['items'].append(self.item_duplicate_id)
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_invalid_type(self):
        self.invalid_type = '123'
        self.parent_data['items'][0]['id'] = self.invalid_type
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_invalid_parent_id(self):
        self.invalid_parent_id = '123'
        self.parent_data['items'][0]['parentId'] = self.invalid_parent_id
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_parent_id_not_exist(self):
        response = self.client.post(
            self.url,
            data=self.children_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_import_where_parent_is_file(self):
        for item in (self.parent_data, self.children_data):
            self.client.post(
                self.url,
                data=item,
                format='json',
            )
        self.data_where_parent_is_file = {
            "items": [
                {
                    "type": "FOLDER",
                    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df8",
                    "parentId": self.children_data['items'][0]['id'],
                },
            ],
            "updateDate": "2022-02-01T12:00:00Z",
        }
        response = self.client.post(
            self.url,
            data=self.data_where_parent_is_file,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_invalid_folder_size(self):
        self.parent_data['items'][0]['size'] = 234
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)
        pass

    def test_invalid_file_size(self):
        self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        invalid_size = -345
        self.children_data['items'][0]['size'] = invalid_size
        response = self.client.post(
            self.url,
            data=self.children_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_folder_not_exist_url(self):
        self.parent_data['items'][0]['url'] = '/url/2'
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_file_invalid_url(self):
        self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        invalid_url = 'dsgdlkfg'
        self.children_data['items'][0]['url'] = invalid_url
        response = self.client.post(
            self.url,
            data=self.children_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_invalid_date(self):
        invalid_date = '234'
        self.parent_data['updateDate'] = invalid_date
        response = self.client.post(
            self.url,
            data=self.parent_data,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)


class ItemGetDeleteTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.uuid = '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1'
        self.children_uuid = 'd515e43f-f3f6-4471-bb77-6b455017a2d2'
        self.url_get_item = reverse('api:get_item', kwargs={'uuid': self.uuid})
        self.url_delete_item = reverse(
            'api:delete_item',
            kwargs={'uuid': self.uuid}
        )
        for batch in IMPORT_BATCHES:
            with self.subTest(data=batch):
                self.client.post(
                    '/imports',
                    data=batch,
                    format='json',
                )

    def test_get_excepted_tree(self):
        response = self.client.get(self.url_get_item)
        self.assertEqual(response.status_code, HTTP_200_OK)
        answer = json.loads(response.content)
        deep_sort_children(answer)
        deep_sort_children(EXPECTED_TREE)
        self.assertEqual(answer, EXPECTED_TREE)

    def test_delete_item(self):
        response = self.client.delete(self.url_delete_item)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Item.objects.filter(pk=self.uuid).count(), 0)
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertEqual(History.objects.all().count(), 0)

    def test_get_invalid_uuid(self):
        invalid_uuid = '123'
        url = reverse('api:get_item', kwargs={'uuid': invalid_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_delete_invalid_uuid(self):
        invalid_uuid = '123'
        url = reverse('api:delete_item', kwargs={'uuid': invalid_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)


class ItemUpdatesTests(APITestCase):
    def setUp(self):
        super().setUp()
        for batch in IMPORT_BATCHES:
            with self.subTest(data=batch):
                self.client.post(
                    '/imports',
                    data=batch,
                    format='json',
                )

    def test_invalid_date(self):
        invalid_date = '123'
        url = f'/updates?date={invalid_date}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_updated_parent_folder_date(self):
        date_folder_before_update = IMPORT_BATCHES[0]['updateDate']
        uuid = IMPORT_BATCHES[0]['items'][0]['id']
        for batch in IMPORT_BATCHES:
            with self.subTest(data=batch):
                self.client.post(
                    '/imports',
                    data=batch,
                    format='json',
                )
        date_folder_after_update = DateTimeField().to_representation(
            Item.objects.get(pk=uuid).date,
        )
        self.assertNotEqual(
            date_folder_before_update,
            date_folder_after_update,
        )


class HistoryTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.uuid = '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1'
        for batch in IMPORT_BATCHES:
            with self.subTest(data=batch):
                self.client.post(
                    '/imports',
                    data=batch,
                    format='json',
                )

    def test_invalid_date(self):
        self.invalid_date = '123'
        url = (
            f'/node/{self.uuid}/history?dateStart={self.invalid_date}&'
            f'dateEnd=2022-02-03T00:00:00Z'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESPONSE_VALIDATION_ERROR)

    def test_history(self):
        excepted_response = {
            'items':
                [
                    {
                        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                        'parentId': None,
                        'type': 'FOLDER',
                        'date': '2022-02-01T12:00:00Z',
                        'url': None,
                        'size': None,
                    },
                    {
                        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                        'parentId': None,
                        'type': 'FOLDER',
                        'date': '2022-02-02T12:00:00Z',
                        'url': None,
                        'size': 384,
                    },
                    {
                        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                        'parentId': None,
                        'type': 'FOLDER',
                        'date': '2022-02-03T12:00:00Z',
                        'url': None,
                        'size': 1920,
                    },
                    {
                        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                        'parentId': None,
                        'type': 'FOLDER',
                        'date': '2022-02-03T15:00:00Z',
                        'url': None,
                        'size': 1984,
                    },
                ],
        }
        self.date_start = '2022-02-01T00:00:00Z'
        self.date_end = '2022-02-03T15:00:00Z'
        url = (
            f'/node/{self.uuid}/history?dateStart={self.date_start}&'
            f'dateEnd={self.date_end}'
        )
        response = self.client.get(url)
        answer = json.loads(response.content)
        self.assertEqual(answer, excepted_response)
