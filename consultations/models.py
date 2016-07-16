# -*- coding: utf-8 -*-

from django.db import models, transaction
from django.contrib.auth.models import Group, User
from django.utils import timezone

from tinymce.models import HTMLField

from thromboass_webapp.utils import get_preview

class ShortQuestionMixin(object):
    def __unicode__(self):
        return get_preview(self.question)    
        
class FAQ(models.Model, ShortQuestionMixin): 
    question = HTMLField(u'Вопрос') 
    answer = HTMLField(u'Ответ')
    
    is_on_faq_page = models.BooleanField(u'Показывать на странице faq', default=True)
    is_on_item_page = models.BooleanField(u'Показывать на странице товара', default=False) 
        
    class Meta:
        verbose_name = u"FAQ"
        verbose_name_plural = u"FAQs"
       
class Consultation(models.Model, ShortQuestionMixin):
    name = models.CharField(u'Имя', max_length=255)
    email = models.EmailField(u'Email', max_length=255)
    is_answered = models.BooleanField(u'На вопрос ответили', default=False)
    question = models.TextField(u'Вопрос') 
    answer = models.TextField(u'Ответ', null=True, blank=True)
    created_at = models.DateTimeField(u'Дата и время создания', default=timezone.now)
    
    #TODO: down't show in admin
    answered_consultant = models.ForeignKey('Consultant', null=True, blank=True)
    answered_datetime = models.DateTimeField(u'Дата и время ответа', null=True, blank=True)
    
    class Meta:
        verbose_name = u"Консультация"
        verbose_name_plural = u"Консультации"

def _save_user_group(user):
    group = Group.objects.get(name='consultants') #SHOULD BE ALREADY CREATED BEFORE ! -> do it in admin
    user.groups.add(group) 
    user.is_staff = True
    user.save(update_fields=['is_staff', ])
       
class ConsultantManager(models.Manager):
    @transaction.atomic
    def create_with_user(self, *args, **kwargs):
        user = User.objects.create_user(kwargs.get('email'), kwargs.get('email'), kwargs.get('password'))
        return self.create(user=user) 
        
    def create(self, *args, **kwargs):
        consultant = super(ConsultantManager, self).create(*args, **kwargs)
        _save_user_group(consultant.user)
        return consultant
               
class Consultant(models.Model):
    user = models.ForeignKey('auth.User')    

    def save(self, *args, **kwargs):
        print not hasattr(self, 'pk') 
        print not self.pk
        is_new = not hasattr(self, 'pk') or not self.pk
        consultant = super(Consultant, self).save(*args, **kwargs)
        if is_new: _save_user_group(self.user)
        return consultant
        
    def __unicode__(self):
        return self.user.username
        
    class Meta:
        verbose_name = u"Консультант"
        verbose_name_plural = u"Консультанты"        
    
