from django.shortcuts import render, redirect
from . import models
from django.db.models import Q, Count, Case, When, Value, BooleanField, F
from django.http import Http404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout


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
    
    view = False
    username = request.user    
    print(username)
    if is_student(username) or (request.user.is_authenticated == False):
        view = False
    elif is_ta(username) or is_admin(username):
        view = True
    try:
        submission_object = models.Submission.objects.filter(assignment = assignment_id)




        
        assignment_object = models.Assignment.objects.get(id = assignment_id)
    except models.User.DoesNotExist:
        raise ValueError(f"This is not valid assignment", assignment_id)
    
    #   for TA 
    try:
        assigned_grader = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        raise ValueError(f"grader {username} is not exists")

    # How many total submissions there are to this assignment(assignment_id)
    submission_total = submission_object.count()

    # # How many of submissions are assigned to "you"
    # if is_admin(username):
    #     assigned_assignment = submission_object.count()
    #     print(submission_object.count())
    assigned_assignment = submission_object.filter(grader = assigned_grader).count()




    
    print(assigned_assignment)
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
                  'id': assignment_id,
                  'view': view
                  })

def submissions(request, assignment_id):
    
    user = request.user
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
    if is_ta(user):
        submission_info = submission_object.filter(grader = assigned_grader
                                                ).order_by('author__username'
                                                ).annotate(author_username = F('author__username'),
                                                        submit_file = F('file'),
                                                        get_score = F('score'),
                                                        user_id = F('id')
                                                ).values("author_username", "submit_file", "get_score", "user_id" )
    elif is_admin(user):
        submission_info = submission_object.order_by('author__username'
                                                        ).annotate(author_username = F('author__username'),
                                                                submit_file = F('file'),
                                                                get_score = F('score'),
                                                                user_id = F('id')
                                                                ).values("author_username", "submit_file", "get_score", "user_id")
        print(submission_info)
    return render(request, "submissions.html",
                {
                    'submission_info': submission_info,
                    'assignment_title': assignment_title,
                    'assignment_point': assignment_point,
                    'assignment_id': assignment_id
                })

# Phase 5
def profile(request):
    user = request.user
    
    # assignment = models.Assignment.objects.all().annotate(
    #     graded = Case()
    # )
    
    try:
        if is_ta(user):            
            viewpint = "ta"
            assignments_list = models.Assignment.objects.all().annotate(
                assigned_count = Count('submission__grader' , filter=Q(submission__grader__username = user)),
                
                total = Count('submission__author'),
                isValid = Case(When(deadline__lt = timezone.now(), then=Value(True)),
                                    default=Value(False),
                                    output_field=BooleanField())
                ).values('title', 'assigned_count', 'total', 'isValid', 'id')
        # When viewed by the administrative user, 
        # it should show the graded and total number of submissions 
        # (ignoring who grades each submission).
        elif is_admin(user):
            viewpoint  = "admin"
            assignments_list = models.Assignment.objects.all().annotate(
            assigned_count = Count('submission__author', filter=~Q(submission__score = None)),
            total = Count('submission__author'),
            isValid = Case(When(deadline__lt = timezone.now(), then=Value(True)),
                                default=Value(False),
                                output_field=BooleanField())
            ).values('title', 'assigned_count', 'total', 'isValid', 'id')
        elif is_student(user):
            viewpoint = "student"
            # assignments_list = models.Assignment.objects.all().annotate(
            #                 total = Count('submission__author'),
            #                 isValid = Case(When(deadline__lt = timezone.now(), then=Value(True)),
            #                                     default=Value(False),
            #                                     output_field=BooleanField())
            #                 ).values('title', 'assigned_count', 'total', 'isValid', 'id')
            
            submissions_list = models.Submission.objects.all().filter(author = user)
            assignments_list = models.Assignment.objects.all()
            for assignment in assignments_list:                
                if assignment.deadline < timezone.now():
                    due = True                        
                    try:    #due 
                        assignment_submissions = submissions_list.get(assignment=assignment)
                        score = assignment.weight * assignment_submissions.score / assignment.points
                    except: #missing
                        score = "Missing"
                else:
                    #   Not due
                    due = False
                    score = "Not Due"
                print(score)
            
    except:
        raise Http404(f" Please check, grader, author, deadline ")
    return render(request, 
                  "profile.html",
                  {
                      "assignments": assignments_list,
                      "username": user,
                      "viewpoint": viewpoint
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
    print("request = ", request)
    
    if request.method == "POST":
        try:
            user = authenticate(username=request.POST["username"], password=request.POST["password"])  
            if user is not None:
                login(request, user)
                return redirect("/profile/")
            else:
                print("user is none ")
                return render(request, "login.html")
        except ValidationError as e:
            print(e)
    else:
        return render(request, "login.html")

def logout_form(request):
    logout(request)
    # Redirect to a success page.
    return redirect("/profile/login/")

def is_student(user):
    return user.groups.filter(name="Students").exists()




    

def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists()




    

def is_admin(user):
    return user.is_superuser