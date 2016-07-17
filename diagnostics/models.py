# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField

from thromboass_webapp.utils import get_preview

def get_next_question_number():
    return TestQuestion.objects.count() + 1

class JSONMixin(object):
    def to_json(self):
        json_ = self.__dict__.copy()
        del json_['_state']  # Deleting standard django model _state field with meta information
        for key in json_.keys(): # Delete cached fields
            if 'cache' in key: del json_[key]
        return json_
            
class TestQuestion(models.Model, JSONMixin):
    question = HTMLField(u'Вопрос')
    order_number = models.IntegerField(u'Порядковый номер', default=get_next_question_number)
    
    def __unicode__(self):
        return u'Вопрос №{}'.format(self.order_number)
        
    class Meta:
        verbose_name = u"Вопрос"
        verbose_name_plural = u"Вопросы" 
            
class TestAnswer(models.Model, JSONMixin):
    question = models.ForeignKey('TestQuestion')
    answer = HTMLField(u'Ответ')
    order_number = models.IntegerField(u'Порядковый номер', default=1)
    score = models.IntegerField(u'Балл', default=0)
    
    def __unicode__(self):
        return u'Ответ №{}'.format(self.order_number)

    class Meta:
        verbose_name = u"Ответ"
        verbose_name_plural = u"Ответы" 
                        
class TestResult(models.Model, JSONMixin):
    score = models.IntegerField(u'Балл', default=0)
    result = HTMLField(u'Результат')
    video = models.CharField('Video', max_length=255, null=True, blank=True)
    image = models.CharField(u'Фото', max_length=255, null=True, blank=True)
        
    related_questions = models.ManyToManyField('consultations.FAQ', verbose_name=u'Типовые вопросы')
    related_articles = models.ManyToManyField('content.Article', verbose_name=u'Релевантные статьи')
    
    def to_json(self):
        json_ = super(TestResult, self).to_json()
        for key in ['related_questions', 'related_articles']:
            del json_[key]
        json_['solutions'] = [solution.to_json() for solution in self.testresultsolution_set()]
        return json_
        
    def __unicode__(self):
        return get_preview(self.result)

    class Meta:
        verbose_name = u"Результат"
        verbose_name_plural = u"Результаты"         
        

class TestResultSolution(models.Model):
    result = models.ForeignKey('TestResult', verbose_name=u'Результат')
    icon = models.ImageField(u'Иконка', upload_to='media/')
    description = models.TextField(u'Описание')
    
    def __unicode__(self):
        return get_preview(self.description)

    class Meta:
        verbose_name = u"Решение"
        verbose_name_plural = u"Решения"     
 
class TestToUserManager(models.Manager):
    def start_new_test(self, **kwargs):
    # close prev unfinished tests if exist by setting its end_datetime
    # create new one
    
    def get_next_step(self, **kwargs):
    # if has no tests, start new one
    # get last test by start_datetime
    # if test has no not-answered questions, close it and show result (check if result already calculated)
    # if test has not-answered questions, return one
    # entities should know their types
    
    def answer2question(self, **kwargs):
    # get last test
    # if it finished, unfinnish it
    # get last question. if has gap btw questions, raise error
    # answer question
         
class TestToUser(models.Model):
    user = models.ForeignKey('auth.User')
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(null=True, blank=True)
    result = models.ForeignKey('TestResult', null=True, blank=True)
    
    objects = TestToUserManager()
    
    @property
    def is_completed(self):
        return not not self.end_datetime

class TestQuestionToUser(models.Model):
    test2user = models.ForeignKey('TestResult')
    created_at = models.DateTimeField(default=timezone.now)
    question = models.ForeignKey('TestQuestion')
    answer = models.ForeignKey('TestAnswer')      
