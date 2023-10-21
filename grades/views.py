from django.shortcuts import render
from . import models
# Create your views here.

def assignments(request):
    assignments = models.Assignment.objects.all()
    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

def index(request, assignment_id):

    assignments = models.Assignment.objects.filter(id=assignment_id).count()
    total_assignment = models.Assignment.objects.count()
    # How many total submissions there are to this assignment(assignment_id)
    submission_total = models.Submission.objects.filter(assignment=assignment_id).count()
    submission_object = models.Submission.objects.filter(assignment=assignment_id)

    # How many of submissions are assigned to "you" with a name of ta1
    assign_submission = models.Submission.objects.filter(id=assignment_id)
    print("assign", assign_submission)
    total_submissions = models.Submission.objects.filter(id=assignment_id, grader='ta1').count()

    # How many total students there are
    total_student = models.Group.objects.get(name="Students").user_set.count()

    print("assignment id = " ,assignment_id)
    print("total = ", total_submissions)
    return render(request, 
                 "index.html",
                 {'assignments': assignments,
                  'total_assignment': total_assignment,
                  'total_student': total_student,
                  'submissions': submission_total,
                  'sub_object': submission_object,
                  'assigned_submission': assign_submission
                  })

def login_form(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
