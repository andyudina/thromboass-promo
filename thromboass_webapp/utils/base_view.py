# -*- coding: utf-8 -*-

from django.views.generic import View
from django.http import JsonResponse

_BAD_REQUEST = 400
_ERRORS = {
    'not_enough_fields': u'Заполните все обязательные поля',
    'already_answered': u'На эту консультацию уже ответили',
    'already_in_faq': u'Уже добавлена в FAQ',
    'question_not_found': u'Такого вопроса не существует',
    'answer_not_found': u'Такого ответа не существует',
    'answer_and_question_dont_match': u'Такого ответа на этот вопрос не существует',
    'cant_skip_questions': u'Нельзя пропустить вопрос'
}

class ParamsValidationError(ValueError):
    pass
    
class BaseView(View):
    def transform(self, val):
        if val.lower() in ['false', 'true']:
            return val.lower() == 'true'
        return val
        
    def validate_necessary_params(self, got_params, expected_params):
        filtered_params = self.filter_params(got_params, expected_params)
        if len(filtered_params) < len(expected_params):
            missed_params = [param for param in expected_params if filtered_params.get(param) is None]
            raise ParamsValidationError(missed_params)
        return filtered_params
            
    def filter_params(self, request_dict, FIELDS):
        return  {field: self.transform(request_dict.get(field)) for field in FIELDS if request_dict.get(field)}
        
    def error(self, error_code, error_fields=[], status_code=_BAD_REQUEST):
        error_ = {
            'message': _ERRORS.get(error_code),
            'code': error_code,
            'fields': error_fields,
        }
        return JsonResponse(error_, status=status_code)
