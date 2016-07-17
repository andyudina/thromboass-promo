# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField

from thromboass_webapp.utils import get_preview
from thromboass_webapp.utils.base_model import JSONMixin

def get_next_question_number():
    return TestQuestion.objects.count() + 1

            
class TestQuestion(models.Model, JSONMixin):
    question = HTMLField(u'Вопрос')
    order_number = models.IntegerField(u'Порядковый номер', default=get_next_question_number)
    
    def __unicode__(self):
        return u'Вопрос №{}'.format(self.order_number)
        
    class Meta:
        verbose_name = u"Вопрос"
        verbose_name_plural = u"Вопросы" 

    def to_json(self):
        json_ = super(TestQuestion, self).to_json()
        return {
            'type': 'question',
            'question': json_,
            'answers': [answer.to_json() for answer in self.testanswer_set.order_by('order_number')],
        }
                    
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
        json_['solutions'] = [solution.to_json() for solution in self.testresultsolution_set.all()]
        return {
            'type': 'result',
            'result': json_,
            'related_questions': [question.to_json() for question in self.related_questions.all()],
            'related_articles': [article.to_json() for article in self.related_articles.all()]
        }
        
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
    def _close_unfinished_tests4user(self, user):
        self.filter(user=user, end_datetime__isnull=True).update(end_datetime=timezone.now())
          
    def start_new_test(self, **kwargs):
        # close prev unfinished tests if exist by setting its end_datetime
        user = kwargs.get('user')
        self._close_unfinished_tests4user(user)
        # create new one
        return self.create(user=user)
    
    def _get_last_test4user(self, user):
        last_tests = self.filter(user=user).order_by('-start_datetime')[:1]
        if last_tests: return last_tests[0]
        return self.create(user=user)
   
    def get_next_step(self, **kwargs):
        # if has no tests, start new one
        # get last test by start_datetime
        user = kwargs.get('user')
        test = self._get_last_test4user(user)
        
        if test.answered_questions_count < TestQuestion.objects.count(): # if test has not-answered questions, return one
             return test.get_next_question() 
        # if test has no not-answered questions, close it and show result (check if result already calculated)
        return test.get_result()        
        # entities should know their types
    
    def answer2question(self, **kwargs):
        user, answer = [kwargs.get(key) for key in ['user', 'answer']]
        # get last test
        test = self._get_last_test4user(user)
        # if it finished, unfinnish it
        if test.is_completed: test.restart()
        # get next question. if has gap btw questions, raise error
        next_question = test.get_next_question()
        if next_question.order_number < answer.question.order_number:
            raise ValueError
        test.answer(answer)
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
        
    @property
    def answered_questions_count(self):
        return self.testquestiontouser_set.count()
     
    def answer(self, answer):
        try:
            user2question = self.testquestiontouser_set.get(question=answer.question) 
            user2question.answer = answer
            user2question.answered_at = timezone.now()
            user2question.save(update_fields=['answer', 'answered_at', ])
        except TestQuestionToUser.DoesNotExist:
            self.testquestiontouser_set.create(question=answer.question, answer=answer)
          
           
    def count_score(self):
        return self.testquestiontouser_set.aggregate(
             models.Sum('answer__score')
        )['answer__score__sum'] or 0
        
    def restart(self):
        self.end_datetime = None
        self.save(update_fields=['end_datetime', ]) 
              
    def get_next_question(self):
        last_order_number = self.testquestiontouser_set.aggregate(
            models.Max('question__order_number'))['question__order_number__max'] or 0
        return TestQuestion.objects.get(order_number = last_order_number + 1)
        #try:
        #    return TestQuestion.objects.get(order_number = last_order_number + 1)
        #except TestQuestion.DoesNotExist: # assume we are trying to get last one -> normally s
        #    return TestQuestion.objects.get(order_number = last_order_number)
        
    def get_result(self):
        if self.end_datetime and self.result:
            return self.result
        score = self.count_score()
        result = TestResult.objects.get(score=score)
        self.result = result
        self.end_datetime = timezone.now()
        self.save(update_fields=['result', 'end_datetime'])
        return result

class TestQuestionToUser(models.Model):
    test2user = models.ForeignKey('TestToUser')
    answered_at = models.DateTimeField(default=timezone.now)
    question = models.ForeignKey('TestQuestion')
    answer = models.ForeignKey('TestAnswer')      
