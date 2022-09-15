from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from items.models import Item
from .unit_test import IMPORT_BATCHES, EXPECTED_TREE


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
            "items": [
                {
                    "type": "FOLDER",
                    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                    "parentId": None
                }
            ],
            "updateDate": "2022-02-01T12:00:00Z"
        }
        self.children_data = {
            "items": [
                {
                    "type": "FOLDER",
                    "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
                }
                ],
            "updateDate": "2022-02-02T12:00:00Z"
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

    def test_duplicate_id_one_request(self):
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

    def test_invalid_parent_type(self):

        pass

    def test_invalid_folder_size(self):
        pass

    def test_invalid_file_size(self):
        pass

    def test_invalid_date(self):
        pass



class ItemTests(APITestCase):



    def test_get_item(self):
        data = {
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'type': 'FOLDER',
            'date': '2022-02-01T12:00:00Z',
            'url': None,
            'size': None,
            'parent': None,
        }
        excepted_data = {
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'type': 'FOLDER',
            'date': '2022-02-01T12:00:00Z',
            'url': None,
            'size': None,
            'children': [],
        }
        Item.objects.create(**data)
        url = reverse('api:get_item', kwargs={'uuid': data['id']})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, excepted_data)

    def test_delete_item(self):
        data = {
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'type': 'FOLDER',
            'date': '2022-02-01T12:00:00Z',
            'url': None,
            'size': None,
            'parent': None,
        }
        Item.objects.create(**data)
        url = reverse('api:delete_item', kwargs={'uuid': data['id']})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Item.objects.filter(pk=data['id']).count(), 0)
