# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from django.core.cache import cache

from content.models import Item, Article, ArticleItem
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
        
    def test_article(self):
        # set up: create article
        article = {
            'title': 'test',
            'preview': 'test'
        }
        
        acticle_items = [
            #Единый текстовый блок;
            {
                'type': 'text',
                'value': '[text] test'
            },
            #Заголовки;
            {
                'type': 'title',
                'value': '[title] test',
            },
            #Подзаголовки;
            {
                'type': 'subtitle',
                'value': '[subtitle] test',
            },
            #Цитата;
            {
                'type': 'quote',
                'value': '[quote] test',
            },
            #Выжимка для акцентирования внимания;
            {
                'type': 'abstract',
                'value': '[abstract] test',
            },
            #Cписок литературы
            {
                'type': 'literature_link',
                'value': '[literature_link-1] test 1',
            },
            #Cписок литературы
            {
                'type': 'literature_link',
                'value': '[literature_link-2] test 2',
            },
            #Ссылки на дополнительные статьи
            {
                'type': 'extra_article_link',
                'value': '[extra_article_link-1] test 1',
            },
            #Ссылки на дополнительные статьи
            {
                'type': 'extra_article_link',
                'value': '[extra_article_link-2] test 2',
            },    
            #Графический контент        
            {
                'type': 'graphcontent',
                'value': '[graphcontent] test',
            },
            #Фото;
            {
                'type': 'photo',
                'value': '[photo] test',
            },
            #Иллюстрация
            {
                'type': 'illustration',
                'value': '[illustration] test',
            },            
        ]
        article = Article.objects.create(**article)
        for item in acticle_items:
            ArticleItem.objects.create(article=article, **item)
             
        # render article
        result = article.render()
        for item in acticle_items:
            self.assertIn(item['value'], result)

        # delete article            
        Article.objects.all().delete()
        ArticleItem.objects.all().delete()
        
       
        
