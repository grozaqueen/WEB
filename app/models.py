from collections import Counter

from django.db import models
from django.conf import settings
from django.db.models import Sum, IntegerField
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, default='avatar.jpg', upload_to='avatars/')
    login = models.CharField(max_length=30)


class Tag(models.Model):
    tag = models.CharField(max_length=20)


class QuestionManager(models.Manager):
    def new_questions_list(self):
        return self.order_by('date').reverse()

    def hot_questions_list(self):
        return self.annotate(
            total_rating=Coalesce(Sum('questionrating__mark', output_field=IntegerField()), 0)).order_by(
            '-total_rating')

    def find_by_tag(self, tag_name):
        return self.prefetch_related('tags').filter(tags__tag=tag_name)

    def search(self, question_id):
        return self.filter(id=question_id).first()


class Question(models.Model):
    def rating_count(self):
        rate_sum = QuestionRating.objects.filter(post=self).aggregate(Sum('mark'))
        return rate_sum['mark__sum'] if rate_sum['mark__sum'] is not None else 0

    def get_tags(self):
        tag_list = self.tags.all()
        tags = []
        for i in range(len(tag_list)):
            tags.append(tag_list[i].tag)
        return tags

    def answers_count(self):
        return Answer.objects.list_answers_count(self.pk)

    title = models.CharField(max_length=256)
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    date = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    objects = QuestionManager()


class AnswerManager(models.Manager):
    def list_answers_count(self, question_id):
        return self.filter(question=question_id).count()

    def answers_list(self, question_id):
        return self.filter(question=question_id).annotate(
            total_rating=Coalesce(Sum('answerrating__mark', output_field=IntegerField()), 0)).order_by('total_rating').reverse()

class Answer(models.Model):
    def rating_count(self):
        r_sum = AnswerRating.objects.filter(post=self).aggregate(Sum('mark'))
        return r_sum['mark__sum'] if r_sum['mark__sum'] is not None else 0

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_correct = models.BooleanField(null=True)

    objects = AnswerManager()


class QuestionRatingManager(models.Manager):
    def search(self, question_id, profile_id):
        return self.filter(post=question_id, profile=profile_id).first()
    def search_by_mark(self, question_id, mark):
        return self.filter(post=question_id, mark=mark)


class QuestionRating(models.Model):
    mark = models.IntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Question, on_delete=models.CASCADE)

    objects = QuestionRatingManager()

    class Meta:
        unique_together = ['profile', 'post']


class AnswerRatingManager(models.Manager):
    def search(self, answer_id, profile_id):
        return self.filter(post=answer_id, profile=profile_id).first()

    def search1(self, profile_id):
        return self.filter(profile=profile_id)

    def search_by_mark(self, answer_id, mark):
        return self.filter(post=answer_id, mark=mark)


class AnswerRating(models.Model):
    mark = models.IntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Answer, on_delete=models.CASCADE)

    objects = AnswerRatingManager()

    class Meta:
        unique_together = ['profile', 'post']