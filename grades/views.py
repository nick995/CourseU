from django.shortcuts import render
from . import models
from django.db.models import Count
from django.http import Http404, HttpResponse
# Create your views here.

def assignments(request):
    assignments = models.Assignment.objects.all()
    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

def index(request, assignment_id):

    try:    
        # How many total submissions there are to this assignment(assignment_id)
        submission_total = models.Submission.objects.filter(assignment=assignment_id).count()
        # How many of submissions are assigned to "you" with a name of ta1
        assigned = models.Submission.objects.filter(assignment=assignment_id).filter(grader__username = 'ta1').count()
        # How many total students there are
        total_student = models.Group.objects.get(name="Students").user_set.count()
        
        assignment_title = models.Assignment.objects.get(id = assignment_id).title
        total_points = models.Assignment.objects.get(id = assignment_id).points
        due_month = models.Assignment.objects.get(id = assignment_id).deadline.strftime('%B')
        due_day = models.Assignment.objects.get(id = assignment_id).deadline.strftime('%d')
        description = models.Assignment.objects.get(id = assignment_id).description
    except:
        raise Http404("...")
    return render(request, 
                 "index.html",
                 {
                  'total_student': total_student,
                  'submissions': submission_total,
                  'assigned': assigned,
                  'assignment_title': assignment_title,
                  'total_points': total_points,
                  'due_day': due_day,
                  'due_month': due_month,
                  'description': description
                  })

def login_form(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
