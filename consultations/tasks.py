# -*- coding: utf-8 -*-

from __future__ import absolute_import
import inspect

from celery import shared_task
from django.utils import timezone

from thromboass_webapp.settings import INFO_EMAIL, CONSULTANT_EMAIL
from thromboass_webapp.utils.email import SendgridError, send_email
from thromboass_webapp.utils import log, generate_email_url
from consultations.models import Consultation

class SendEmailTaskFabric(object):
    def _get_already_sent_flag(self, consultation):
        raise NotImplemented
     
    def _get_message(self, consultation):
        raise NotImplemented
        
    def _form_email_kwargs(self, **kwargs):
        raise NotImplemented
     
    def _update_datetime(self, consultation):
        raise NotImplemented
        
    def _get_consultation(self, consultation_id):
        try:
            return Consultation.objects.get(id = consultation_id)
        except Consultation.DoesNotExist:
            log(level='error', message='[CELERY NOTIFY CONSULTANT] no consultation with id {}'.format(consultation_id))
            return 
            
    def _is_already_sent(self, consultation):
        print inspect.getsourcelines(getattr(self, '_get_already_sent_flag')) 
        if self._get_already_sent_flag(consultation):
            log(level='error', message='[CELERY NOTIFY CONSULTANT] consult with id {} already sent'.format(consultation.id))
            return True
        return False
        
    def _send_email(self, consultation):
        message = self._get_message(consultation) 
        try:
            send_email(**self._form_email_kwargs(message=message, consultation=consultation))
        except SendgridError as e:
            log(level='error', message='[CELERY NOTIFY CONSULTANT] sendgrid returned error: {}'.format(e.args[0]))
            return False
        return True
                               
    def as_task(self):
        def _task_function(consultation_id):
            consultation = self._get_consultation(consultation_id)
            if consultation is None: 
                return
            if self._is_already_sent(consultation): 
                return
            if not self._send_email(consultation):
                return 
            self._update_datetime(consultation)
        return _task_function

class SendNotifiEmail(SendEmailTaskFabric):
    def _get_already_sent_flag(self, consultation):
        return consultation.is_notification_sent
     
    def _get_message(self, consultation):
        return u'''<p>Имя: {}</p>
                   <p>Email: {}</p>
                   <p>Вопрос: {}</p>
                   <p>-----------</p>
                   <p><a href="{}">Консультация в админке</a></p>
               '''.format(consultation.name, consultation.email, consultation.question, 
                          generate_email_url('admin', 'consultations', 'consultation', consultation.id))
        
    def _form_email_kwargs(self, **kwargs):
        return dict(
            from_email=INFO_EMAIL, 
            subject=u'Новая консультация на сайте Тромбо АСС',
            to_email = CONSULTANT_EMAIL,
            content = kwargs.get('message'),
            content_type = 'text/html'
        )
     
    def _update_datetime(self, consultation):
        consultation.notification_sent_at = timezone.now()
        consultation.save(update_fields=['notification_sent_at', ])
        
@shared_task                                          
def send_notification2consultant(*args, **kwargs):
    return SendNotifiEmail().as_task()(*args, **kwargs)

class SendConsultAnswer(SendEmailTaskFabric):
    def _get_already_sent_flag(self, consultation):
        return consultation.is_answered
     
    def _get_message(self, consultation):
        return u'''<p>Ответ на вашу консультацию</p>
                   <p>{}</p>
               '''.format(consultation.answer)
        
    def _form_email_kwargs(self, **kwargs):
        return dict(
            from_email=INFO_EMAIL, 
            subject=u'Ответ на консультацию на сайте Тромбо АСС',
            to_email = kwargs.get('consultation').email,
            content = kwargs.get('message'),
            content_type = 'text/html'
        )
     
    def _update_datetime(self, consultation):
        consultation.answer_sent_at = timezone.now()
        consultation.save(update_fields=['answer_sent_at', ])

@shared_task                                          
def send_consult_answer(*args, **kwargs):
    return SendConsultAnswer().as_task()(*args, **kwargs)

