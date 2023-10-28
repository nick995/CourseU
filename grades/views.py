from django.shortcuts import render
from . import models
from django.db.models import Count
<<<<<<< HEAD
from django.http import Http404, HttpResponse
=======
from django.http import Http404

>>>>>>> 3ceca5ab7554479f1cb64ff0bffa643f6fb888dc
# Create your views here.

def assignments(request):
    assignments = models.Assignment.objects.all()

    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

def index(request, assignment_id):
    try:
        submission_object = models.Submission.objects.filter(assignment = assignment_id)
        assignment_object = models.Assignment.objects.get(id = assignment_id)
    except models.User.DoesNotExist:
        raise ValueError(f"This is not valid assignment", assignment_id)

    print(assignment_id)
    print("assignment object = ", assignment_object)
    print("id = ", models.Assignment.objects.model)

    try:
        grader = models.User.objects.get(username="ta1")
    except models.User.DoesNotExist:
        raise ValueError(f"grader (ta1) is not exists")

<<<<<<< HEAD
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
=======
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
    
>>>>>>> 3ceca5ab7554479f1cb64ff0bffa643f6fb888dc
    return render(request, 
                 "index.html",
                 {
                  'total_student': total_student,
                  'submissions': submission_total,
                  'assigned': assigned_assignment,
                  'assignment_title': assignment_title,
<<<<<<< HEAD
                  'total_points': total_points,
                  'due_day': due_day,
                  'due_month': due_month,
                  'description': description
=======
                  'total_points': assignment_point,
                  'deadline': assginment_deadline,
                  'description': assignment_description
                  })

# Phase 5
def profile(request):
    # passing query set 
    assignments_list = models.Assignment.objects.all()

    

    username = "ta1"
    submissions_count = models.Submission.objects.filter(grader__username = username).values("assignment").annotate(count = Count("assignment"))

    return render(request, 
                  "profile.html",
                  {
                      'assignment_list': assignments_list,
                      'submissions_count': submissions_count,
                      'username': username
>>>>>>> 3ceca5ab7554479f1cb64ff0bffa643f6fb888dc
                  })

def login_form(request):
    return render(request, "login.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
