from django.core.management import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from app.models import Profile, QuestionRating, AnswerRating, Tag, Question, Answer

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("num", type=int)

    def handle(self, *args, **kwargs):
        num = kwargs['num']
        users = []
        for i in range(num + 1):
            users.append(User(
                username=fake.unique.user_name()[:fake.random_int(min=3, max=8)] + fake.unique.user_name()[:fake.random_int(min=3, max=7)] + f'{fake.random_int(min=0, max=1000)}',
                email=fake.email(),
                password=fake.password(special_chars=False),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            ))
        User.objects.bulk_create(users)
        self.stdout.write("Completed with users")
        users = User.objects.all()

        profiles = []
        for i in range(num + 1):
            unique_login = f"{fake.first_name()}_{fake.last_name()}"
            profile = Profile(user=users[i], login=unique_login)
            profiles.append(profile)

        Profile.objects.bulk_create(profiles)
        self.stdout.write("Completed with profiles")
        profiles = Profile.objects.all()

        _tags = []
        for _ in range(num + 1):
            tag = Tag(tag=fake.word())
            _tags.append(tag)

        Tag.objects.bulk_create(_tags)
        self.stdout.write("Completed with tags")
        _tags = Tag.objects.all()

        questions = []
        for i in range(num * 10 + 1):
            title = fake.sentence(nb_words=fake.random_int(min=2, max=7))
            text = fake.text(max_nb_chars=300)
            date = str(fake.date_time_this_decade())
            profile = profiles[fake.random_int(min=0, max=num-1)]

            question = Question(title=title, text=text, date=date, profile=profile)
            questions.append(question)

        Question.objects.bulk_create(questions)
        questions = Question.objects.all()

        for question in questions:
            num_tags = fake.random_int(min=1, max=3)
            tag_indices = [fake.random_int(min=0, max=num - 1) for _ in range(num_tags)]
            selected_tags = [_tags[index] for index in tag_indices]
            question.tags.set(selected_tags)

        self.stdout.write("Completed with questions")

        answers = []
        for i in range(num * 100 + 1):
            question = questions[fake.random_int(min=0, max=num * 10 - 1)]
            text = fake.text(max_nb_chars=500)
            date = str(fake.date_time_this_decade())
            profile = profiles[fake.random_int(min=0, max=num - 1)]

            # Определение корректности ответа
            if fake.random_int() % 10 == 0:
                is_correct = True
            else:
                is_correct = False

            answer = Answer(question=question, text=text, date=date, profile=profile, is_correct=is_correct)
            answers.append(answer)

        Answer.objects.bulk_create(answers)
        self.stdout.write("Completed with answers")
        answers = Answer.objects.all()

        question_ratings = []
        unique_pairs1 = set()
        for i in range(num * 100 + 1):
            mark = -1 if fake.random_int(min=0, max=100) % 4 == 0 else 1
            profile = profiles[fake.random_int(min=0, max=num - 1)]
            post = questions[i%(num * 10 - 1)] if i < num * 10 else questions[fake.random_int(min=0, max=num * 10 - 1)]
            pair = (profile.id, post.id)

            if pair not in unique_pairs1:
                unique_pairs1.add(pair)
                question_rating = QuestionRating(mark=mark, profile=profile, post=post)
                question_ratings.append(question_rating)

        QuestionRating.objects.bulk_create(question_ratings)
        self.stdout.write("Completed with Question ratings")

        answer_ratings = []
        unique_pairs = set()

        for i in range(num * 100 + 1):
            mark = -1 if fake.random_int(min=0, max=100) % 4 == 0 else 1
            profile = profiles[fake.random_int(min=0, max=num - 1)]
            post = answers[i] if i < num * 100 else answers[fake.random_int(min=0, max=100 * num - 1)]

            pair = (profile.id, post.id)

            if pair not in unique_pairs:
                unique_pairs.add(pair)
                answer_rating = AnswerRating(mark=mark, profile=profile, post=post)
                answer_ratings.append(answer_rating)

        AnswerRating.objects.bulk_create(answer_ratings)
        self.stdout.write("Completed with Answer ratings")