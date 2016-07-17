from django.http import HttpResponse, Http404

from thromboass_webapp.utils.base_view import BaseView, ParamsValidationError
from diagnostics.models import TestQuestion, TestAnswer, TestResult, TestToUser, TestQuestionToUser

_NOT_FOUND = 404
class StartDiagnosticView(BaseView):
   def post(self, request, *args, **kwargs):
       TestToUser.objects.start_new_test(user=request.user)
       return HttpResponse()
       
class NextStepView(BaseView):
   def get(self, request, *args, **kwargs):
       next_step = TestToUser.objects.get_next_step(user=request.user)
       return JsonResponse(next_step.to_json())
       
class AnswerQuestionView(BaseView):
   def post(self, request, *args, **kwargs):
        try:
            question = TestQuestion.objects.get(id=kwargs.get('question_id'))
        except TestQuestion.DoesNotExist:
            return self.error('question_not_found', [], _NOT_FOUND)
              
        EXPECTED_PARAMS = ['answer', ]
        try:
            params = self.validate_necessary_params(request.POST, EXPECTED_PARAMS)
        except ParamsValidationError as e:
            return self.error('not_enough_fields', e.args[0])
             
        try:
            answer = TestAnswer.objects.get(id=params.get('answer'))
        except TestAnswer.DoesNotExist:
            return self.error('answer_not_found', [], _NOT_FOUND)
            
        if anwer.question_id != question.id:
            return self.error('answer_and_question_dont_match', [], _NOT_FOUND)
        try:
            TestToUser.objects.answer2question(user=request.user, answer=answer)
        except ValueError:
            return self.error('cant_skip_questions') 
        return HttpResponse()
            
                   
           
       
              
       
