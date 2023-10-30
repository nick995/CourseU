from django.shortcuts import render, redirect
from . import models
from django.db.models import Q, Count, Case, When, Value, BooleanField, F
from django.http import Http404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError, ObjectDoesNotExist


# Create your views here.

def assignments(request):
    try:
        assignments = models.Assignment.objects.all()
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignments")
    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

def index(request, assignment_id):
    user = "ta1"
    try:
        submission_object = models.Submission.objects.filter(assignment = assignment_id)
        assignment_object = models.Assignment.objects.get(id = assignment_id)
    except models.User.DoesNotExist:
        raise ValueError(f"This is not valid assignment", assignment_id)

    try:
        assigned_grader = models.User.objects.get(username=user)
    except models.User.DoesNotExist:
        raise ValueError(f"grader {user} is not exists")

    # How many total submissions there are to this assignment(assignment_id)
    submission_total = submission_object.count()

    # How many of submissions are assigned to "you" with a name of ta1
    assigned_assignment = submission_object.filter(grader = assigned_grader).count()

    # How many total students there are
    try:
        total_student = models.Group.objects.get(name="Students").user_set.count()
    except models.Group.DoesNotExist:
        raise ValueError(f"Student group is not found")
    
    try:
        assignment_title = assignment_object.title
        assignment_point = assignment_object.points
        assginment_deadline = assignment_object.deadline
        assignment_description = assignment_object.description
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignment with id {assignment_id}")
    
    return render(request, 
                 "index.html",
                 {
                  'total_student': total_student,
                  'submissions': submission_total,
                  'assigned': assigned_assignment,
                  'assignment_title': assignment_title,
                  'total_points': assignment_point,
                  'deadline': assginment_deadline,
                  'description': assignment_description,
                  'id': assignment_id
                  })

def submissions(request, assignment_id):
    
    user = "ta1"
    #The "Student" column has the submission's author's name
    #The "Submission" link should point to the submission's file.url field. This link won't work, however, until Homework 5.
    #The input field should have a name of grade-X where X is the submission's ID and have a value which is the submission's score.
    try:
        assignment_object = models.Assignment.objects.get(id = assignment_id)
        submission_object = models.Submission.objects.filter(assignment = assignment_id)
    except models.User.DoesNotExist:
        raise ValueError(f"This is not valid assignment", assignment_id)

    try:
        assigned_grader = models.User.objects.get(username=user)
    except models.User.DoesNotExist:
        raise ValueError(f"grader {user} is not exists")
    
    try:
        assignment_title = assignment_object.title
        assignment_point = assignment_object.points
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignment with id {assignment_id}")
    
    submission_info = submission_object.filter(grader = assigned_grader
                                            ).order_by('author__username'
                                            ).annotate(author_username = F('author__username'),
                                                       submit_file = F('file'),
                                                       get_score = F('score'),
                                                       user_id = F('id')
                                            ).values("author_username", "submit_file", "get_score", "user_id" )
    return render(request, "submissions.html",
                  {
                      'submission_info': submission_info,
                      'assignment_title': assignment_title,
                      'assignment_point': assignment_point,
                      'assignment_id': assignment_id
                  })

# Phase 5
def profile(request):
    username = "ta1"
    
    try:    
        assignments_list = models.Assignment.objects.all().annotate(
            assigned_count = Count('submission__grader' , filter=Q(submission__grader__username = username)),
            total = Count('submission__author'),
            isValid = Case(When(deadline__lt = timezone.now(), then=Value(True)),
                                default=Value(False),
                                output_field=BooleanField())
            ).values('title', 'assigned_count', 'total', 'isValid', 'id')
    except:
        raise Http404(f" Please check, grader, author, deadline ")
        
    return render(request, 
                  "profile.html",
                  {
                      "assignments": assignments_list,
                      "username": username
                  })

@require_POST
def grade (request, assignment_id):



    if request.method == "POST":
        try:
            for x in request.POST:
                if x[:6] == "grade-":
                    submission = models.Submission.objects.get(id = x[6])
                    try:
                        submission.score = float(request.POST[x])
                    except ValueError as e:
                        print(e, "Insert valid floating-point number.")
                        submission.score = None
                    submission.full_clean()
                    submission.save()
        except ValidationError as e:
            print(e)
    try:
        return redirect(f"/{assignment_id}/submissions")
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignment with id {assignment_id}")

def login_form(request):
    return render(request, "login.html")
