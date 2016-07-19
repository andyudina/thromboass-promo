# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.template import loader, Context
from tinymce.models import HTMLField

from thromboass_webapp.utils.base_model import JSONMixin

class MainPageCarousel(models.Model):
    video = models.CharField('Video', max_length=255, null=True, blank=True)
    image = models.CharField(u'Фото', max_length=255, null=True, blank=True)
    title = models.CharField(u'Заголовок', max_length=255)
    text = HTMLField(u'Текст')
    url = models.CharField('Url', max_length=255)
    order_number = models.IntegerField(u'Порядковый номер')
    
    def __unicode__(self):
        return u'Слайд {}: {}'.format(self.order_number, self.title)
        
    class Meta:
        verbose_name = u"Слайд карусели на главной"
        verbose_name_plural = u"Слайды карусели на главной"
        
class DeseaseInfo(models.Model):
    alias = models.CharField(u'Url alias', max_length=255)
    url_title = models.CharField(u'Заголовок ссылки', max_length=255)
    
    desease_info_title = models.CharField(u'О Заболевании: заголовок', max_length=255)
    desease_info_text = HTMLField(u'О Заболевании: текст')
    desease_info_image = models.ImageField(u'О Заболевании: графический контент', upload_to='media/')
    
    diagnostic_title = models.CharField(u'Диагностика: заголовок', max_length=255)
    diagnostic_url   = models.CharField(u'Диагностика: ссылка на карту', max_length=255)
    diagnostic_text = HTMLField(u'Диагностика: текст')
    diagnostic_image = models.ImageField(u'Диагностика: графический контент', upload_to='media/')
    

    cure_title = models.CharField(u'Лечение: заголовок', max_length=255)
    cure_url   = models.CharField(u'Лечение: ссылка на карту', max_length=255)
    cure_text = HTMLField(u'Лечение: текст')
    cure_image = models.ImageField(u'Лечение: графический контент', upload_to='media/')

    relevant_articles = models.ManyToManyField('Article', blank=True, verbose_name=u'Релевантные статьи')
    popular_questions = models.ManyToManyField('consultations.FAQ', blank=True, verbose_name=u'Популярные вопросы')
    
    def __unicode__(self):
        return self.url_title
        
    class Meta:
        verbose_name = u"Страница заболевания"
        verbose_name_plural = u"Страницы заболевания"
        
       
class Item(models.Model):
    description_title = models.CharField(u'Описание препарата и состав: Заголовок', max_length=255)
    description_text = HTMLField(u'Описание препарата и состав: текст')
    description_infographic = models.ImageField(u'Описание препарата и состав: Инфографика', upload_to='media/')
            
    application = HTMLField(u'Показания к применению')
    
    operating_principle_title = models.CharField(u'Принцип действия препарата: Заголовок', max_length=255)
    operating_principle_text = HTMLField(u'Принцип действия препарата: текст')
    operating_principle_infographic = models.ImageField(u'Принцип действия препарата: Инфографика', upload_to='media/')
    
    video = models.CharField('Video', max_length=255, null=True, blank=True)
    image = models.CharField(u'Фото', max_length=255, null=True, blank=True)
    short_title = models.CharField(u'Заголовок 2-го порядка', max_length=255)
    
    def __unicode__(self):
        return u"Продукт"
        
    class Meta:
        verbose_name = u"Продукт"
        verbose_name_plural = u"Продукты"  
        
class Test(models.Model, JSONMixin):
    text = HTMLField(u'Текст')
    title = models.CharField(u'Заголовок', max_length=255)
    short_title = models.CharField(u'Заголовок второго порядка', max_length=255)
    video = models.CharField('Video', max_length=255, null=True, blank=True)
    image = models.CharField(u'Фото', max_length=255, null=True, blank=True)

    def __unicode__(self):
        return u"Тест"
        
    class Meta:
        verbose_name = u"Тест"
        verbose_name_plural = u"Тесты"
               
class Article(models.Model, JSONMixin):
    _templates = {}
    
    title = models.CharField(u'Заголовок', max_length=255) #TODO: detailed blocks??
    #text = HTMLField(u'Текст')  
    preview = models.TextField(u'Превью')
    photo = models.ImageField(u'Фото', upload_to='media/')
    image = models.ImageField(u'Иллюстрация', upload_to='media/')
    
    created_at = models.DateTimeField(u'Время публикации', default=timezone.now)
    relevant_articles = models.ManyToManyField('self')
    is_on_item_page = models.BooleanField(u'Показывать на странице товара', default=False)
    
    def __unicode__(self):
        return self.title

    def preproc(self):
        article_items = []
        for item in self.articleitem_set.all():
            if not 'link' in item.type:
                # если не линкующиеся элементы, ничего с ними не делаем
                article_items.append({'type': item.type, 'item': item})
                continue
            # собираем идущие подряд линки (ссылки на доп статьи/ список литры) в одну группу
            last_element = article_items and article_items[-1]
            if last_element and last_element.get('type') == item.type: #продолжаем существующую группу
                last_element.get('items').append(item)
            else: #начинаем новую
                article_items.append(
                    {
                        'type': item.type,
                        'items': [item,]
                    }    
                ) 
        return article_items
               
    def render(self):
        def _get_template_name(type_):
            return 'content/article/{}.html'.format(type_)
            
        data = self.preproc()
        templates = []
        for element in data:
            if self._templates.get(element.get('type')):
                template = self._templates[element.get('type')]
            else:
                template = _get_template_name(element.get('type'))
                template = loader.get_template(template)
                self._templates[element.get('type')] = template
            context = Context(element)
            templates.append(template.render(context))
            
        main_template = loader.get_template(_get_template_name('main'))
        return main_template.render(Context({'blocks': templates}))

    class Meta:
        verbose_name = u"Статья"
        verbose_name_plural = u"Статьи"
         

ARTICLE_ITEM_CHOICES = (
    ('text', u'Единый текстовый блок'),
    ('title', u'Заголовок'),
    ('subtitle', u'Подзаголовок'),
    ('quote', u'Цитата'),
    ('abstract', u'Выжимка для акцентирования внимания'),
    ('literature_link', u'Cписок литературы'),
    ('extra_article_link', u'Ссылки на дополнительные статьи'),
    ('graphcontent', u'Графический контент'),
    ('photo', u'Фото'),
    ('illustration', u'Иллюстрация'),      
)
        
class ArticleItem(models.Model):
    article = models.ForeignKey('Article', verbose_name='Статья')
    value = models.TextField(u'Контент')
    type = models.CharField(u'Тип', max_length=255, choices=ARTICLE_ITEM_CHOICES)
    
    def __unicode__(self):
        return u'{} {} статьи "{}"'.format(
            self.get_type_display(),
            self.id,
            self.article.title
        ) 
        
    class Meta:
        verbose_name = u"Элемент статьи"
        verbose_name_plural = u"Элементы статьи"   
