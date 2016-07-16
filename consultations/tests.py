import json

from django.test import TestCase, Client
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from consultations.models import Consultation, FAQ, Consultant, CONSULTANT_PERMISSION_NAME
from thromboass_webapp.utils import generate_random_sequence

BASE_URL = '/ajax/consultations/'
SUCCESS_STATUS = 200
BAD_REQUEST_STATUS = 400
FORBIDDEN_CODE = 403

CONSULT_USERNAME = 'consultant@consultant.test'
CONSULT_PASSWORD = 'consultant'

class ConsultationsTestCase(TestCase):
    @classmethod
    def _create_group4consultants(cls):
        consultants_group, created = Group.objects.get_or_create(name='consultants')
        ct = ContentType.objects.get_for_model(Consultation)
        for permission_action in ['add', 'change', 'delete']:
            permission = Permission.objects.create(
                 codename='can_{}_consultation'.format(permission_action),
                 name='Can {} consultation'.format(permission_action),
                 content_type=ct)
            consultants_group.permissions.add(permission)
            
    @classmethod
    def setUpClass(cls):
        cls._create_group4consultants()
        cls.consultant = Consultant.objects.create_with_user(email=CONSULT_USERNAME, password=CONSULT_PASSWORD)
        
    def setUp(self):
        self.client = Client()
        
    def test_create_consultant(self):
        consultant = Consultant.objects.create(email='test@test.test', password='test')
        permission = Permisson.objects.get(name=CONSULTANT_PERMISSION_NAME)
        self.assertEqual(consultant.groups.filter(permission_id=permission.id).count(), 1)
        
    def _ask_consultation(self, **kwargs):
        return self.client.post(BASE_URL, kwargs)
        
    def test_ask_consultation__success_obj_created(self):
        unique_name = generate_random_sequence()
        response = self._ask_consultation(name=unique_name, email='test@test.ru', question='this is test question')
        self.assertEqual(response.statuse_code, SUCCESS_STATUS)
        self.assertEqual(Consultation.objects.filter(name=unique_name).count(), 1)
                
    def test_ask_consultation__not_enough_fields(self):
        response = self._ask_consultation(email='test@test.ru', question='this is test question')
        self.assertEqual(response.statuse_code, BAD_REQUEST_STATUS)
        self.assertItemsEqual(json.loads(response.content)['fields'], ['name', ])
     
    def _create_consultation(self, **kwargs):
        return Consultation.objects.create(
            name=kwargs.get('name', 'test'), 
            email=kwargs.get('email', 'test@test.ru'), 
            question=kwargs.get('question', 'this is test question')
        )
        
    def _post_answer_to_consult(self, answer):
        consultation = self._create_consultation()
        return consultation, self.client.post(
            BASE_URL + '{}/'.format(consultation.id),
            dict(answer=answer)
        ) 
             
    def test_answer_consultation__success(self):
        self.client.login(username=CONSULT_USERNAME, password=CONSULT_PASSWORD) 
        answer = generate_random_sequence()
        consultation, reponse = self._post_answer_to_consult(answer)
        self.assertEqual(response.statuse_code, SUCCESS_STATUS)
        consultation = Consultation.objects.get(id=consultation.id)
        self.assertTrue(consultation.answer, answer)
        self.assertTrue(consultation.is_answered)
        self.assetEqual(consultation.answered_consultant_id, self.consultant.id)
        
    def test_answer_consultation__not_enough_rights(self):
        answer = generate_random_sequence()
        consultation, reponse = self._post_answer_to_consult(answer)
        self.assertEqual(response.status_code, FORBIDDEN_CODE)
        consultation = Consultation.objects.get(id=consultation.id)
        self.assertIsNone(consultation.answer)
        self.assertFalse(consultation.is_answered)
        
    def _add_to_faq(self, question='test', **kwargs):
        consultation = self._create_consultation(question=question)
        return consultation, self.client.post(
            BASE_URL + '{}/2faq/'.format(consultation.id),
            kwargs
        ) 
                
    def test_add_consultation_to_faq__success(self):
        self.client.login(username=CONSULT_USERNAME, password=CONSULT_PASSWORD)
        is_on_faq_page = False
        is_on_item_page = True
        question = generate_random_sequence()
        answer = generate_random_sequence()
        _, response = self._add_to_faq(
            question,
            is_on_faq_page=is_on_faq_page,
            is_on_item_page=is_on_item_page,
            answer=answer
        )
        self.assertEqual(response.status_code, SUCCESS_STATUS)
        faq = FAQ.objects.get(question=question)
        self.assertEqual(faq.answer, answer)
        self.assertEqual(faq.is_on_faq_page, is_on_faq_page)
        self.assertEqual(faq.is_on_item_page, is_on_item_page)
        
    def test_add_consultation_to_faq__not_enough_rights(self):
        question = generate_random_sequence()
        _, response = self._add_to_faq(
            question,
            is_on_faq_page=is_on_faq_page,
            is_on_item_page=is_on_item_page,
            answer=answer
        )    
        self.assertEqual(response.status_code, FORBIDDEN_CODE)
        self.assertEqual(FAQ.objects.count(question=question), 0)  
    
    
   
