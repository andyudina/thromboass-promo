from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from thromboass_webapp.utils.base_view import BaseView, ParamsValidationError
from consultations.models import Consultation, FAQ
from consultations.tasks import send_notification2consultant, send_consult_answer

class ConsultView(BaseView):
    def post(self, request, *args, **kwargs):
        EXPECTED_PARAMS = ['name', 'email', 'question', ]
        try:
            params = self.validate_necessary_params(request.POST, EXPECTED_PARAMS)
        except ParamsValidationError as e:
            return self.error('not_enough_fields', e.args[0])
        consultation = Consultation.objects.create(**params)
        send_notification2consultant.delay(consultation.id)
        return HttpResponse()

class StaffOnlyView(BaseView):
    # TODO: assumes that there are only 2 types of user: admins(superuser) and consultants -> basic staff
    # TODO: doesn't check permission for consultations directly
    # TODO: so can broke security on next growth -> better rewrite proper checks
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)
                    
class ConsultAnswerView(StaffOnlyView):
    def post(self, request, *args, **kwargs):
        try:
            consultation = Consultation.objects.get(id=kwargs.get('id'))
        except Consultation.DoesNotExist:
            return Http404
            
        if consultation.is_answered:
            return self.error('already_answered')
              
        EXPECTED_PARAMS = ['answer', ]
        try:
            params = self.validate_necessary_params(request.POST, EXPECTED_PARAMS)
        except ParamsValidationError as e:
            return self.error('not_enough_fields', e.args[0])
        
        params.update({
            'answered_consultant': request.user,
        })
        Consultation.objects.filter(id=consultation.id).update(**params)
        send_consult_answer.delay(consultation.id)
        return HttpResponse()
            
class Consut2FAQView(StaffOnlyView):
    def post(self, request, *args, **kwargs):
        try:
            consultation = Consultation.objects.get(id=kwargs.get('id'))
        except Consultation.DoesNotExist:
            return Http404
            
        if not request.POST.get('answer') and not consultation.answer:
            return self.error('not_enough_fields', ['answer', ])
            
        if hasattr(consultation, 'faq') and consultation.faq:
            return self.error('already_in_faq')
              
        EXPECTED_PARAMS = ['is_on_faq_page', 'is_on_item_page', 'answer']
        params = {key: request.POST.get(key) for key in EXPECTED_PARAMS if request.POST.get(key) is not None}
        params.update({
            'source_consultation': consultation,
            'question': consultation.question,
        })
        
        if params.get('answer'):
            Consultation.objects.filter(id=kwargs.get('id')).update(answer=params.get('answer'))
        else:
            params['answer'] = consultation.answer
                
        FAQ.objects.create(**params)
        
        return HttpResponse()   
