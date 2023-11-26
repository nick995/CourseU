from django.shortcuts import render, redirect
from . import models
from django.db.models import Q, Count, Case, When, Value, BooleanField, F
from django.http import Http404, HttpResponse
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

# Create your views here.

def is_student(user):
    return user.groups.filter(name="Students").exists()
def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists()
def is_admin(user):
    return user.is_superuser
def is_ta_admin(user):
    if user.groups.filter(name="Teaching Assistants").exists() or user.is_superuser:
        return True
    else:
        return False

@login_required(login_url="/profile/login/")
def assignments(request):
    print("assignments")
    try:
        assignments = models.Assignment.objects.all()
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignments")
    return render(request, 
                  "assignments.html",
                  dict(assignments=assignments))

@login_required(login_url="/profile/login/") 
def index(request, assignment_id):
    print("index")

    view = False
    username = request.user    
    try:
        submission_object = models.Submission.objects.filter(assignment = assignment_id)
        assignment_object = models.Assignment.objects.get(id = assignment_id)
    except models.User.DoesNotExist:
        raise ValueError(f"This is not valid assignment", assignment_id)
    #   for ta and student
    try:
        assignment_title = assignment_object.title
        assignment_point = assignment_object.points
        assginment_deadline = assignment_object.deadline
        assignment_description = assignment_object.description
    except models.Assignment.DoesNotExist:
        raise Http404(f"Could not find assignment with id {assignment_id}")
    
    if is_student(username):
        student_data = {}
        view = "student"
        #   case1.  submitted, grade
        #   case2.  submitted,ungraded 
        #   case3.  submitted, not due 
        #   case4.  not submitted, not due  
        #   case5.  not submitted, past due  
        
        try:
            print(assignment_id)
            #   if there's no submission, go to except
            submission_object = models.Submission.objects.get(assignment = assignment_id, author = username)
            # print("test = ", submission_object.file)
            #   case1
            if submission_object.score is not None:
                student_data["file"] = submission_object.file
                student_data["score"] = submission_object.score
                student_data["point"] = assignment_object.points
                student_data["case"] = "case1"
                student_data["earn"] = submission_object.score / assignment_object.points * assignment_object.weight
            #   case2
            else:
                student_data["file"] = submission_object.file
                #   if past due 
                if assignment_object.deadline < timezone.now():
                    student_data["case"] = "case2"
                else:
                    student_data["case"] = "case3"
        except:
            #   case 5
            if assignment_object.deadline < timezone.now():
                student_data["announce"] = "You did not submit this assignment and received 0 points."
                student_data["case"] = "case5"
            #   case 4
            else:
                student_data["announce"] = "No current submission."
                student_data["case"] = "case4"

        return render(request,
                      "index.html",
                      {
                        'student_data': student_data,
                        'view': view,
                        'assignment_title': assignment_title,
                        'total_points': assignment_point,
                        'deadline': assginment_deadline,
                        'description': assignment_description,
                        'id': assignment_id,

                      })
    elif is_ta(username) or is_admin(username):
        view = "ta_admin"
    elif (request.user.is_authenticated == False):
        pass
    
    #   for TA 
    try:
        assigned_grader = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        raise ValueError(f"grader {username} is not exists")

    # How many total submissions there are to this assignment(assignment_id)
    submission_total = submission_object.count()

    # # How many of submissions are assigned to "you"
    assigned_assignment = submission_object.filter(grader = assigned_grader).count()
    # How many total students there are
    try:
        total_student = models.Group.objects.get(name="Students").user_set.count()
    except models.Group.DoesNotExist:
        raise ValueError(f"Student group is not found")
    return render(request, 
                 "index.html",
                 {
                  'submissions': submission_total,
                  'total_student': total_student,
                  'assigned': assigned_assignment,
                  'assignment_title': assignment_title,
                  'total_points': assignment_point,
                  'deadline': assginment_deadline,
                  'description': assignment_description,
                  'id': assignment_id,
                  'view': view
                  })
    
@user_passes_test(is_ta_admin)
@login_required(login_url="/profile/login/")
def submissions(request, assignment_id):
    print("submissions")
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

    return render(request, "submissions.html",
                {
                    'submission_info': submission_info,
                    'assignment_title': assignment_title,
                    'assignment_point': assignment_point,
                    'assignment_id': assignment_id
                })

@login_required(login_url="/profile/login/")
def profile(request):
    print("profile")

    user = request.user
    
    # assignment = models.Assignment.objects.all().annotate(
    #     graded = Case()
    # )
    try:
        
        if is_ta(user):            
            viewpoint = "ta"
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
            submissions_list = models.Submission.objects.all().filter(author = user)
            assignments_list = models.Assignment.objects.all()
            total_avilable = 0
            total_earn = 0
            assignment_dic = {}
            
            for assignment in assignments_list:                
                
                
                if assignment.deadline < timezone.localtime():
                    # print("assignment title = ", assignment.title, "points = ", assignment.points, "deadline = ", assignment.deadline)
                    # print(timezone.localtime())
                    due = True                        
                    try:    #due 
                        
                        assignment_submissions = submissions_list.get(assignment=assignment)
                        #   for 
                        total_earn += assignment.weight * assignment_submissions.score / assignment.points
                        #   for displaying
                        score = str(assignment_submissions.score / assignment.points * 100) + "%"
                        #   
                        total_avilable += assignment.weight
                    except: 
                        try:
                            if submissions_list.get(assignment = assignment).score == None:
                            #   ungraded
                                score = "Ungraded"
                        except:
                            #   missing
                            total_avilable += assignment.weight
                            score = "Missing"
                else:
                    #   Not due
                    due = False
                    score = "Not Due"
                    assignment.points = 0
                    
                assignment_dic[assignment.title] = [assignment.pk , score]
            print(total_earn)
            print(total_avilable)
            return render(request, 
                        "profile.html",
                        {
                            "assignments": assignment_dic,
                            "username": user,
                            "viewpoint": viewpoint,
                            "finalgrade": round(total_earn/total_avilable* 100, 1)
                        })
                
                

    except:
        raise Http404(f" Please check, grader, author, deadline ")
    return render(request, 
                  "profile.html",
                  {
                      "assignments": assignments_list,
                      "username": user,
                      "viewpoint": viewpoint
                  })


@user_passes_test(is_ta_admin)
@login_required(login_url="/profile/login/")
@require_POST
def grade (request, assignment_id):
    print("grade")
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
    
    if request.method == "POST":
        print(request.POST['next'])
        try:
            user = authenticate(username=request.POST["username"], password=request.POST["password"])  
            if user is not None:
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST['next'])
                else:
                    return redirect('/profile/')
            else:
                #   loginfail = re render
                return render(request, "login.html",{
                    "error": "Username and password do not match"
                })
        except ValidationError as e:
            print(e)
    elif request.method == "GET":
        if 'next' in request.GET:
            get_next = request.GET["next"]
            print("get next = ", get_next)
            #   pass that to the login.html
            return render(request, "login.html",
                        {
                            "next": get_next
                            }
                        )
        else:
            return redirect("/profile/")
    else:
        return render(request, "login.html")

def logout_form(request):
    logout(request)
    # Redirect to a success page.
    return redirect("/profile/login/")

@user_passes_test(is_student)
def submit(request, id):
    
    assignment_object = models.Assignment.objects.get(id = id)
    
    #   if it is already past due, return a 400 response.
    if assignment_object.deadline < timezone.now():
        # Acts just like HttpResponse but uses a 400 status code.
        raise ValidationError("Due date is passed")
    else:
        if request.FILES.get('file', False):
            file = request.FILES['file']
        else:
            return redirect(f"/{id}/")
            #   change to new submit
        try:
            submission_object = models.Submission.objects.get(assignment = id)
            submission_object.file = file
            submission_object.save()
        except:
            #   not submitted yet
            
            submission_object = models.Submission.objects.create(assignment=assignment_object,
                                                                 file = file,
                                                                 author= request.user ,
                                                                 grader= pick_grader(assignment_object),
                                                                 score= None)
            print(submission_object)
            submission_object.save            
        return redirect(f"/{id}/")

def pick_grader(Assignment):
    #   get teaching assistant group -> annotate graded_set as total_assigned -> order by fewest
    #   get first query
    assigend_ta = models.Group.objects.get(name="Teaching Assistants").user_set.all().annotate(
        total_assigned=Count("graded_set")
    ).order_by("total_assigned")[:1].get()
    
    return assigend_ta

def show_upload(request, filename):
    print(filename)
    user = request.user
    submission = models.Submission.objects.get(file = filename)
    if (submission.author == user) or (submission.grader == user) or (is_admin(user)):
        pass
    else:        
        raise PermissionDenied()
    with submission.file.open() as fd:
        response = HttpResponse(fd)
        response["Content-Disposition"] = \
            f'attachment; filename="{submission.file.name}"'
        return response