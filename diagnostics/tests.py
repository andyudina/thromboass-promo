import json

from django.test import TestCase, Client

from diagnostic.models import TestQuestion, TestAnswer, TestResult

BASE_URL = '/ajax/diagnostic/'
SUCCESS_STATUS = 200
BAD_REQUEST_STATUS = 400

class DiagnosticTestCase(TestCase):
    @classmethod
    def _create_test(cls):
        test_questions = [{
            'question': 'test question 2',
            'order_number': 2
        },
        {
            'question': 'test question 1',
            'order_number': 1
        }]
        
        test_answers = [
            [
                {'answer': 'answer 1', 'score': 1, 'order_number': 2},
                {'answer': 'answer 2', 'score': 2, 'order_number': 1}
            ],
            [
                {'answer': 'answer 3', 'score': 1, 'order_number': 2},
                {'answer': 'answer 4', 'score': 2, 'order_number': 1}
            ],
        ]
        
        test_results = [
            {'result': 'result1', 'score': 2},
            {'result': 'result2', 'score': 3},
            {'result': 'result3', 'score': 4}
        ] 
        for i, question in enumerate(test_questions):
            test_question = TestQuestion.objects.create(**question) 
            answers = test_answers[i]
            for answer in answers:
                TestAnswer.objects.create(question=test_question, **answer)
                
        for result in test_results:
            TestResult.objects.create(**result)
                    
    @classmethod
    def setUpClass(cls):
        cls._create_test() #2 questions * 2 answers == 3 results
    
    def setUp(self):
        self.client = Client()
        
    def _init_test(self):
        return self.client.post(
            BASE_URL + 'start/'
        )
        
    def _answer_question(self, **kwargs):
        return self.client.post(
            BASE_URL + 'questions/{}/'.format(kwargs.get('question')),
            {'answer': kwargs.get('answer')}
        )
        
    def _get_next(self):
        response =  self.client.get(
            BASE_URL + 'next/'
        )
        self.assertEqual(response.status_code, SUCCESS_STATUS)
        return json.loads(response)

    def _process_question_success(self, index):
        question = self._get_next()
        self.assertEqual(question.get('type'), 'question')
        self.assertEqual(question.get('question').get('id'), TestQuestion.objects.get(order_number=index).id)
        # answer first question
        response = self._answer_question(
            question=question.get('question').get('id'),
            answer=question.get('question').get('answers')[0].get('id')
        )
        self.assertEqual(response.status_code, SUCCESS_STATUS)
                   
    def test_pass_test__success(self):
        # init
        respone = self._init_test()
        self.assertEqual(response.status_code, SUCCESS_STATUS)
        
        # get&answer questions:
        for index in xrange(2):
            self._process_question_success(index)
            
        #process result
        result = self.get_next()
        self.asserEqual(result.get('type'), 'result')
        self.assertEqual(result.get('result'), 'result3')
        
    def test_pass_test__send_invalid_answer(self):
        NUMERIC_CONSTANT_GREATER_THAN_ANSWERS_NUMBER = 5
        
        # init
        respone = self._init_test()
        self.assertEqual(response.status_code, SUCCESS_STATUS)
        
        # get question
        question = self._get_next()
        self.assertEqual(question.get('type'), 'question')
        
        # send wrong answer
        response = self._answer_question(
            question=question.get('question').get('id'),
            answer=question.get('question').get('answers')[0].get('id') + NUMERIC_CONSTANT_GREATER_THAN_ANSWERS_NUMBER
        )
        self.assertEqual(response.status_code, BAD_REQUEST_STATUS)        
