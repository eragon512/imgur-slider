import unittest
from django.test import Client

from offline_storage.models import *
from offline_storage.views import *

# Create your tests here.
class AlbumDownloadTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_server(self):
        response = self.client.get('/offline/')
        self.assertEqual(response.status_code, 200)

    def test_album_storage(self):
        request = self.client.get('/offline/album/')
        response = album(request,'pyyvA')
        self.assertEqual(response.status_code, 200)
    # still not working right

    def test_form_process(self):
        response = self.client.post('/offline/album/',{'album_url': 'http://imgur.com/a/MUsSI'})
        self.assertEqual(response.status_code, 200)
        #response = album_list(request)
        #response.client = self.client
        #self.assertRedirects(response, reverse("/offline/album/"))
