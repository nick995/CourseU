from django.shortcuts import render
from . import models
from django.db.models import Count
from django.http import Http404

# Create your views here.

def assignments(request):
    assignments = models.Assignment.objects.all()
    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

def index(request, assignment_id):

    submission_object = models.Submission.objects.filter(assignment = assignment_id)
    assignment_object = models.Assignment.objects.get(id = assignment_id)

    try:
        grader = models.User.objects.get(username="ta1")
    except models.User.DoesNotExist:
        raise ValueError(f"grader (ta1) is not exists")

    # How many total submissions there are to this assignment(assignment_id)
    submission_total = submission_object.count()

    # How many of submissions are assigned to "you" with a name of ta1
    assigned_assignment = submission_object.filter(grader = grader).count()

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
                  'description': assignment_description
                  })

def login_form(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
