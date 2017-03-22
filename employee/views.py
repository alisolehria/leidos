from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import profile, projects, skills, staffWithSkills, projectsWithSkills, holidays, alerts, staffAlerts, messageBoard, boardComments
from adminUser.models import location
from django.http import HttpResponse
from django.db.models import Q
from adminUser.forms import HolidaysForm
import datetime
from django.contrib import messages

@login_required
def alerttab_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if project Manager
        return HttpResponse(status=201)
    title = "Alerts"
    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by('-alertID')
    projectListUp = query.staffwithprojects_set.filter(Q(status="Working") & Q(projects_ID__status="Approved"))
    projectListOn = query.staffwithprojects_set.filter(Q(status="Working") & Q(projects_ID__status="On Going"))

    return render(request, 'sideBar/alertTab.html', {"title":title, "alertList":alertList,"projectListOn":projectListOn,"projectListUp":projectListUp})

@login_required
def refresh_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)



    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by(
        '-alertID')

    alertids = {}

    for i, alert in enumerate(alertList):
        if i > 0:
            alertids.update({(alertList[i - 1].alertID): alert})
        else:
            alertids.update({'abc': alert})
    return render(request,'sideBar/refresh.html',{"alertList":alertList,"alertids":alertids})

@login_required
def profile_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if project Manager
        return HttpResponse(status=201)

    info = profile.objects.get(user=username)

    time = datetime.date.today()
    ongoing = info.staffwithprojects_set.filter(Q(startDate__lte=time) & Q(endDate__gte=time) & Q(status="Working")).count()
    upcoming = info.staffwithprojects_set.filter(Q(startDate__gt=time) & Q(status="Working")).count()
    completed = info.staffwithprojects_set.filter(Q(endDate__lt=time) & Q(status="Working")).count()

    skillids = info.staffwithskills_set.values_list('skillID',flat =True)
    skillNames=[]
    skillids = list(set(skillids))
    for id in skillids:
        skillNames.append(skills.objects.get(skillID=id))


    skillhrs = info.staffwithskills_set.all()
    time = datetime.date.today()  # get todays date



    return render(request, 'eprofile/profile.html',{"title":username,"info":query,"ongoing":ongoing,"upcoming":upcoming,"completed":completed,"skillhrs":skillhrs,"skillNames":skillNames,"time":time})

@login_required()
def myprojects_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)
    #completed projects of specific user
    info = profile.objects.get(staffID=query.staffID)
    title = "My Projects"
    list = info.staffwithprojects_set.exclude(status="Not Working")
    if request.POST:
        if 'project' in request.POST:
            project = request.POST.getlist('project')
            return projectprofile_View(request, project[0])
        elif 'staff' in request.POST:
            staff = request.POST.getlist('staff')
            return staffprofile_View(request, staff[0])
    return render(request,'eprojects/myprojects.html',{"list":list,"title":title})

@login_required()
def projectlist_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)

    title = "Projects List"
    list = projects.objects.filter(status="Approved")#get all the objects from profile table which have been approved

    if request.POST:
        if 'project' in request.POST:
            project = request.POST.getlist('project')
            return projectprofile_View(request,project[0])
        elif 'staff' in request.POST:
            staff = request.POST.getlist('staff')
            return staffprofile_View(request, staff[0])
    return render(request,'eprojects/projectlist.html',{"list":list,"title":title})

@login_required()
def upcomingprojectsget_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)
    #upcoming projects of specific user
    time = datetime.date.today()
    title = "Upcoming Projects of " + query.user.first_name + " " + query.user.last_name
    list = query.staffwithprojects_set.filter(Q(startDate__gt=time) & Q(status="Working"))
    return render(request,'eprojects/myprojects.html',{"list":list,"title":title})


@login_required()
def currentprojectsget_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)
    #get ongoing project of specific user
    time = datetime.date.today()
    title = "On Going Projects of " + query.user.first_name + " " + query.user.last_name
    list =  query.staffwithprojects_set.filter(Q(startDate__lte=time) & Q(endDate__gte=time) & Q(status="Working"))
    return render(request,'eprojects/myprojects.html',{"list":list,"title":title})

@login_required()
def completedprojectsget_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)
    #completed projects of specific user
    time = datetime.date.today()
    title = "Completed Projects of " + query.user.first_name + " " + query.user.last_name
    list = query.staffwithprojects_set.filter(Q(endDate__lt=time) & Q(status="Working"))
    return render(request,'eprojects/myprojects.html',{"list":list,"title":title})

@login_required()
def projectprofile_View(request, project_id=None):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)

    if project_id is not None:
        info = projects.objects.get(projectID=project_id)
    # this part takes skills and skill hours req. and puts them in a dict
        skillset = []
        skills = info.skills_set.all()
        skillset = list(skills)

        skillhrset = []
        skillhrs = info.projectswithskills_set.all()
        skillhrset = list(skillhrs)

        skillwithhrs = {}

        i = 0
        while i < len(skillset):
            skillwithhrs.update({skillset[i]: skillhrset[i]})
            i = i + 1
        title = info.projectName

    if request.POST and 'staffNum' in request.POST:
        staff = request.POST.getlist('staffNum')
        project = request.POST.getlist('projectNum')
        proj = projects.objects.get(projectID=project[0])
        alert = alerts.objects.create(fromStaff=query, alertType='Project Request', alertDate=datetime.date.today(),project=proj)
        staffAlerts.objects.create(alertID=alert, staffID=proj.projectManager, status="Unseen")
        messages.success(request,"Project Request Successfull!")
        return projectlist_View(request)

    board = 0
    try:
        id = messageBoard.objects.get(projectID=info)
        board = id.boardID
    except:
        None

    return render(request, 'eprojects/projectprofile.html', {"info":info, "skillwithhrs":skillwithhrs,'user':query,"title":title,"board":board})

@login_required()
def staffprofile_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)

    title = staff_id
    info = profile.objects.get(staffID = staff_id)



    title = info.user.first_name + " " + info.user.last_name

    # this part takes skills and skill hours available and puts them in a dict
    skillset = []
    skills = info.skills_set.all()
    skillset = list(skills)

    skillhrset = []
    skillhrs = info.staffwithskills_set.all()
    skillhrset = list(skillhrs)

    skillwithhrs = {}

    i = 0
    while i < len(skillset):
        skillwithhrs.update({skillset[i]: skillhrset[i]})
        i = i + 1

    return render(request,'eprofile/staffprofile.html',{"info":info,"title":title, "skillwithhrs":skillwithhrs})

@login_required
def alert_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)

    title = "Alerts"


    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)

    if request.POST:
        if 'unseen' in request.POST:
            alertID = request.POST.getlist('unseen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0])&Q(staffID=query.staffID))
            alertObj.update(status="Seen")
        elif 'project' in request.POST:
            project = request.POST.getlist('project')
            return projectprofile_View(request, project[0])

    return render(request,'sideBar/alerts.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def holiday_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if employee
        return HttpResponse(status=201)

    title = "Request Leave"

    admin = profile.objects.get(staffID=1)
    if request.method == "POST":
        form = HolidaysForm(request.POST,user=request.user)
        if form.is_valid():
            hol = form.save(commit=False)
            hol.status="Pending Approval"
            hol.staffID_id = query.staffID
            hol.save()
            alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                          holiday=hol, info="Your Project Request")
            staffAlerts.objects.create(alertID=alert, staffID=admin, status="Unseen")
            messages.success(request, "Leave Requested!")
    else:
        form = HolidaysForm(user=request.user)
    return render(request, 'eprofile/requestholiday.html', {"title":title, "form":form})


@login_required
def requests_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if admin
        return HttpResponse(status=201)

    title = "My Requests"


    alertList = alerts.objects.filter(Q(staff=query.staffID)&Q(alertType="Leave")).order_by('-alertID')
    staff_id = str(query.staffID)



    return render(request,'eprofile/requests.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def messageBoard_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if pm
        return HttpResponse(status=201)

    title = "Message Board"
    allProjects = projects.objects.filter(staffID=query.staffID)
    allBoards = []
    for proj in allProjects:
        try:
            board = messageBoard.objects.get(projectID=proj.projectID)
            allBoards.append(board)
        except:
            None

    return render(request, 'eprojects/message.html', {"title": title,"allBoards":allBoards})

@login_required
def comments_View(request,board_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Employee":  # check if pm
        return HttpResponse(status=201)

    board = messageBoard.objects.get(boardID=board_id)
    comments = boardComments.objects.filter(board_id=board_id)
    title = board.projectID.projectName+"'s Message Board"

    if request.POST:
        comment = request.POST.getlist("comment")
        boardComments.objects.create(board=board,staff=query,comment=comment[0],time=datetime.date.today())
        messages.success(request, "Comment Posted Succesfully")

    return render(request, 'eprojects/comments.html', {"title": title,"comments":comments,"board":board})