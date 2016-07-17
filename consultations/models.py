# -*- coding: utf-8 -*-

from django.db import models, transaction
from django.contrib.auth.models import Group, User
from django.utils import timezone

from tinymce.models import HTMLField

from thromboass_webapp.utils import get_preview
from thromboass_webapp.utils.base_model import JSONMixin

CONSULTANT_GROUP_NAME='consultants'

class ShortQuestionMixin(object):
    def __unicode__(self):
        return get_preview(self.question)    
        
class FAQ(models.Model, ShortQuestionMixin, JSONMixin): 
    source_consultation = models.OneToOneField(
        'Consultation', null=True, blank=True, 
         verbose_name=u"Консультация, откуда появился вопрос"
    )
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
    question = models.TextField(u'Вопрос') 
    answer = models.TextField(u'Ответ', null=True, blank=True)
    created_at = models.DateTimeField(u'Дата и время создания', default=timezone.now)
    
    answered_consultant = models.ForeignKey('auth.User', null=True, blank=True)
    answered_datetime = models.DateTimeField(u'Дата и время ответа', null=True, blank=True)
    notification_sent_at = models.DateTimeField(u'Дата и время отправки уведомления коснультанту', null=True, blank=True)
    answer_sent_at = models.DateTimeField(
        u'Дата и время отправки ответа', 
        null=True, blank=True) #shoudn't be hidden in admin -> need for js check answer logic
    
    @property
    def is_answered(self):
        return not not self.answer_sent_at
        
    @property
    def is_notification_sent(self):
        return not not self.notification_sent_at
        
    class Meta:
        verbose_name = u"Консультация"
        verbose_name_plural = u"Консультации"

def _save_user_group(user):
    group = Group.objects.get(name=CONSULTANT_GROUP_NAME) #SHOULD BE ALREADY CREATED BEFORE ! -> do it in admin
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
      
    objects = ConsultantManager()
    
    def save(self, *args, **kwargs):
        is_new = not hasattr(self, 'pk') or not self.pk
        consultant = super(Consultant, self).save(*args, **kwargs)
        if is_new: _save_user_group(self.user)
        return consultant
        
    def __unicode__(self):
        return self.user.username
        
    class Meta:
        verbose_name = u"Консультант"
        verbose_name_plural = u"Консультанты"        
    
