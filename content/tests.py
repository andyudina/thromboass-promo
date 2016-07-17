from django.test import TestCase, Client
from django.core.cache import cache

from content.models import Item
from thromboass_webapp.utils import generate_random_sequence

BASE_URL = '/item/'

class ContentTestCase(TestCase):
    @classmethod
    def _create_item(cls): 
        cls.random_title = generate_random_sequence()
        Item.objects.create(
            description_title=cls.random_title,
            description_text='test',
            description_infographic='',
            
            application = 'test',
            operating_principle_title = 'test',
            operating_principle_text = 'test',
            operating_principle_infographic = 'test',
            video = '',
            image = '',
            
            short_title = 'test',
        )
        
    @classmethod
    def setUpClass(cls):
        super(ContentTestCase, cls).setUpClass()
        cls._create_item()
        
    def setUp(self):
        self.client = Client()
            
    def test_item_page(self):
        '''check whether our page was rendered properly'''
        cache._cache.flush_all()
        response = self.client.get(BASE_URL)
        self.assertIn('html',  response.get('Content-Type'))
        self.assertIn(self.random_title, response.content)
        
