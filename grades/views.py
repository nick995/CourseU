from django.shortcuts import render
from . import models
from django.db.models import Q, Count, Case, When, Value, BooleanField, F
from django.http import Http404
from django.utils import timezone


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

# Phase 5
def profile(request):


    username = "ta1"
    
    current_time = timezone.now()

    # passing query set 
    # assignments_list = models.Assignment.objects.all().annotate(
    #     assigned_count = Count('submission__grader' , filter=Q(submission__grader__username = username))
    #     ).annotate(total = Count('submission__author')
    #     ).annotate(duedate = Case(When('assignment__deadline__gt',F('datetime.now()')), then =Value(True)),
    #                               default=Value(False),
    #                               output_field=BooleanField).values('title', 'assigned_count', 'total', 'deadline', 'duedate')

    assignments_list = models.Assignment.objects.all().annotate(
        assigned_count = Count('submission__grader' , filter=Q(submission__grader__username = username))
        ).annotate(total = Count('submission__author')
        ).annotate( isValid = Case(When(deadline__lt = current_time, then=Value(True)),
                                    default=Value(False),
                                    output_field=BooleanField()
                                        )
        ).values('title', 'assigned_count', 'total', 'isValid')
    
    # for assignment in assignments_list:
    #     print(assignment["isValid"])
    
    # .annotate(check = Case(When(F('deadline') < timezone.now(), then=Value(False)),
    #                             default=Value(True))
    #     )
    
    
    # for assignment in assignments_list:
        
    #     if assignment["duedate"] < timezone.now():
    #         assignment["valid"] = False
    
    # assignment_list = models.Assignment.objects.all()


    
    # for assignment in assignment_list:
        
    #     if assignment.deadline < timezone.now():
    #         assignment.to_grade = str(UNGRADED COUNT) + " / " + str(GRADED COUNT)
    
    
    # test = models.Assignment.objects.filter(submission__grader__username = username).annotate(gc=Count('submission__grader')).values('title', 'gc')
    
    # submissions_count = models.Submission.objects.filter(grader__username = username).values("assignment").annotate(count = Count("assignment"))
    
    return render(request, 
                  "profile.html",
                  {
                      "assignments": assignments_list
                  })

def login_form(request):
    return render(request, "login.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")