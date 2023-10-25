from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

class Assignment(models.Model):
    # short string for title
    title = models.CharField(max_length=200)
    # long string for the assignment description
    description = models.TextField(blank=True)
    # date and a time.
    deadline = models.DateTimeField()
    # integer weight (which is how much the assignment is worth toward the final grade)
    weight = models.IntegerField()
    # integer number of maximum points(which is how much this assignment is graded out of)
    points = models.IntegerField(
        default=100,
    )
    # for testing
class Submission(models.Model):

    assignment = models.ForeignKey(Assignment,
                                   on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.SET_NULL,
                               related_name='graded_set',
                               null=True, blank=True)
    file = models.FileField()
    score = models.FloatField(blank=True, null=True)

    