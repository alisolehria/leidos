from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import profile, projects, skills, staffWithSkills, projectsWithSkills,staffProjectSkill, holidays, alerts, staffAlerts,staffWithProjects, messageBoard, boardComments
from adminUser.models import location
from django.http import HttpResponse
from django.db.models import Q
from adminUser.forms import ProjectForm, HolidaysForm
import datetime
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
import os.path
from django.conf import settings
from reportlab.lib.colors import PCMYKColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


@login_required
def alerttab_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if project Manager
        return render(request,'errorpermission.html')
    title = "Alerts"
    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by('-alertID')
    projectListUp = query.staffwithprojects_set.filter(Q(status="Working") & Q(projects_ID__status="Approved"))
    projectListOn = query.staffwithprojects_set.filter(Q(status="Working") & Q(projects_ID__status="On Going"))

    return render(request, 'alerts/alertTab.html', {"title":title, "alertList":alertList,"projectListOn":projectListOn,"projectListUp":projectListUp})

@login_required
def refresh_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')



    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by(
        '-alertID')
    alertids = {}

    for i, alert in enumerate(alertList):
        if i > 0:
            alertids.update({(alertList[i - 1].alertID): alert})
        else:
            alertids.update({'abc': alert})
    return render(request,'alerts/refresh.html',{"alertList":alertList,"alertids":alertids})

@login_required
def profile_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if project Manager
        return render(request,'errorpermission.html')

    info = profile.objects.get(user=username)
    time = datetime.date.today()
    ongoing = info.staffwithprojects_set.filter(
        Q(startDate__lte=time) & Q(endDate__gte=time) & Q(status="Working")).count()
    upcoming = info.staffwithprojects_set.filter(Q(startDate__gt=time) & Q(status="Working")).count()
    completed = info.staffwithprojects_set.filter(Q(endDate__lt=time) & Q(status="Working")).count()

    # this part takes skills and skill hours available and puts them in a dict
    skillids = info.staffwithskills_set.values_list('skillID', flat=True)
    skillNames = []
    skillids = list(set(skillids))
    for id in skillids:
        skillNames.append(skills.objects.get(skillID=id))

    skillhrs = info.staffwithskills_set.all()
    time = datetime.date.today()


    return render(request, 'profile/profile.html',{"title":username,"info":query,"ongoing":ongoing,"upcoming":upcoming,"completed":completed,"skillhrs":skillhrs,"skillNames":skillNames,"time":time})

@login_required()
def upcomingprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')
    #upcoming projects of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "Upcoming Projects of " + info.user.first_name + " " + info.user.last_name
    list = info.staffwithprojects_set.filter(Q(startDate__gt=time) & Q(status="Working"))
    return render(request,'projects/myprojects.html',{"list":list,"title":title})


@login_required()
def currentprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')
    #get ongoing project of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "On Going Projects of " + info.user.first_name + " " + info.user.last_name
    list =  info.staffwithprojects_set.filter(Q(startDate__lte=time) & Q(endDate__gte=time) & Q(status="Working"))
    return render(request,'projects/myprojects.html',{"list":list,"title":title})

@login_required()
def completedprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')
    #completed projects of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "Completed Projects of " + info.user.first_name + " " + info.user.last_name
    list = info.staffwithprojects_set.filter(Q(endDate__lt=time) & Q(status="Working"))
    return render(request,'projects/myprojects.html',{"list":list,"title":title})

@login_required()
def projectlist_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = "Projects List"
    list = projects.objects.all() #get all the objects from profile table
    return render(request,'projects/projectlist.html',{"list":list,"title":title})

@login_required()
def projectprofile_View(request, project_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    info = projects.objects.get(projectID=project_id)
    title = info.projectName
    count = info.staffwithprojects_set.filter(status="Working").count()
    # this part takes skills and skill hours req. and puts them in a dict
    skillset = []
    skills = info.skills_set.all()
    skillset = list(skills)
    past = staffWithProjects.objects.filter(projects_ID=project_id)
    past = past.exclude(status="Working")
    current = staffWithProjects.objects.filter(projects_ID=project_id)
    current = current.exclude(status="Not Working")

    skillhrset = []
    skillhrs = info.projectswithskills_set.all()
    skillhrset = list(skillhrs)

    skillwithhrs = {}

    i = 0
    while i < len(skillset):
        skillwithhrs.update({skillset[i]: skillhrset[i]})
        i = i + 1

    if request.POST and 'complete' in request.POST:
        id = request.POST.getlist("complete")
        project = projects.objects.filter(projectID=id[0])
        info = projects.objects.get(projectID=id[0])
        project.update(status="Completed")
        alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                      project=info, info="Project")
        working = info.staffID.all()
        for staff in working:
            employee = profile.objects.get(staffID=staff.staffID)
            staffAlerts.objects.create(alertID=alert, staffID=employee, status="Unseen")

        alertAdmin = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),project=info)
        staffAlerts.objects.create(alertID=alertAdmin, staffID=profile.objects.get(staffID = 1), status="Unseen")
        messages.success(request, "Project Status Changed")
        return projectlist_View(request)
    elif "remove" in request.POST:
        id = request.POST.getlist("remove")
        proj = staffWithProjects.objects.filter(profile_ID=id[0])
        st = profile.objects.get(staffID=id[0])
        proj = proj.filter(projects_ID=project_id)
        proj.update(status="Not Working")
        try:
            skill = staffProjectSkill.objects.filter(Q(projectID_id=info.projectID) & Q(staffID_id=st))
            for sk in skill:
                pskill = info.projectswithskills_set.get(skillID=sk.skillID)
                final = pskill.hoursRequired + sk.hours
                pskill.hoursRequired = final
                sskill = st.staffwithskills_set.get(Q(skillID=sk.skillID) & Q(month=sk.month))
                final = sskill.hoursLeft + sk.hours
                sskill.hoursLeft = final
                pskill.save()
                sskill.save()
        except ObjectDoesNotExist:
            messages.success(request, "No effect to one or many skills")

        alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                      project=info, info="removed from")
        staffAlerts.objects.create(alertID=alert, staffID=profile.objects.get(staffID=id[0]), status="Unseen",
                                   )
        messages.success(request, "Staff Removed")

    elif 'staffNum' in request.POST:
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
    return render(request, 'projects/projectprofile.html', {"title":title,"info":info, "skillwithhrs":skillwithhrs,'user':query,"past":past,"current":current,"count":count,"board":board})

@login_required()
def myprojects_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')
    #completed projects of specific user
    info = profile.objects.get(staffID=query.staffID)
    title = "My Projects"
    list = info.staffwithprojects_set.all()
    print(list.count())
    return render(request,'projects/myprojects.html',{"list":list,"title":title})

@login_required()
def staffprofile_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')


    info = profile.objects.get(staffID = staff_id)
    title = info.user.first_name+" "+info.user.last_name
    time = datetime.date.today()
    ongoing = info.staffwithprojects_set.filter(Q(startDate__lte=time) & Q(endDate__gte=time)).count()
    upcoming = info.staffwithprojects_set.filter(startDate__gt=time).count()
    completed = info.staffwithprojects_set.filter(endDate__lt=time).count()

    skillids = info.staffwithskills_set.values_list('skillID', flat=True)
    skillNames = []
    skillids = list(set(skillids))
    for id in skillids:
        skillNames.append(skills.objects.get(skillID=id))

    skillhrs = info.staffwithskills_set.all()

    return render(request,'employee/staffprofile.html',{"info":info,"title":title,"ongoing":ongoing,"upcoming":upcoming,"completed":completed,"skillhrs":skillhrs,"skillNames":skillNames})

@login_required
def alert_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = "Alerts"
    admin = profile.objects.get(staffID=1)

    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)

    if request.POST:
        if "unseen" in request.POST:
            alertID = request.POST.getlist('unseen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0])&Q(staffID=query.staffID))
            alertObj.update(status="Seen")
        elif "accept" in request.POST:
            staff = request.POST.getlist('accept')
            projectNum = request.POST.getlist('projectNum')
            alertID = request.POST.getlist('seen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0]) & Q(staffID=query.staffID))
            alertObj.update(status="Seen")
            projectAdd = projects.objects.get(projectID=projectNum[0])
            date = request.POST.getlist('selectDate')
            st = profile.objects.get(staffID=staff[0])
            if date == []:
                projSkills =  projectAdd.projectswithskills_set.all()
                for sk in projSkills:
                    dates =  projectAdd.projectswithskills_set.get(skillID=sk.skillID_id)
                    sMonth = dates.startDate.month
                    eMonth = dates.endDate.month
                    try:
                        if dates.hoursRequired > 0:
                            stSkill = st.staffwithskills_set.filter(skillID=sk.skillID)
                            if sMonth is eMonth:
                                hrs = stSkill.get(month=sMonth)
                                initial = hrs.hoursLeft
                                if hrs.hoursLeft >= dates.hoursRequired:
                                    hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                    dates.hoursRequired = 0
                                else:
                                    dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                    hrs.hoursLeft = 0
                                final = initial - hrs.hoursLeft
                                staffProjectSkill.objects.create(projectID= projectAdd, staffID=st,
                                                                 skillID=skills.objects.get(skillID=sk.skillID_id),
                                                                 hours=final,
                                                                 month=sMonth)
                                hrs.save()
                                dates.save()
                            else:
                                for month in range(sMonth, eMonth + 1):
                                    if dates.hoursRequired > 0:
                                        hrs = stSkill.get(month=month)
                                        initial = hrs.hoursLeft
                                        if hrs.hoursLeft >= dates.hoursRequired:
                                            hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                            dates.hoursRequired = 0
                                        else:
                                            dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                            hrs.hoursLeft = 0
                                        final = initial - hrs.hoursLeft
                                        staffProjectSkill.objects.create(projectID= projectAdd, staffID=st,
                                                                         skillID=skills.objects.get(
                                                                             skillID=sk.skillID_id),
                                                                         hours=final, month=month)
                                        hrs.save()
                                        dates.save()

                    except ObjectDoesNotExist:
                        None

                staffWithProjects.objects.create(projects_ID= projectAdd, profile_ID=profile.objects.get(staffID=staff[0]),
                                                 status="Working", startDate= projectAdd.startDate, endDate= projectAdd.endDate)
            else:
                sDate = []
                eDate = []
                for sk in date:
                    dates =  projectAdd.projectswithskills_set.get(skillID=sk)
                    sDate.append(dates.startDate)
                    eDate.append(dates.endDate)
                    sMonth = dates.startDate.month
                    eMonth = dates.endDate.month

                    try:
                        if dates.hoursRequired > 0:
                            stSkill = st.staffwithskills_set.filter(skillID=sk)
                            if sMonth is eMonth:
                                hrs = stSkill.get(month=sMonth)
                                initial = hrs.hoursLeft
                                if hrs.hoursLeft >= dates.hoursRequired:
                                    hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                    dates.hoursRequired = 0
                                else:
                                    dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                    hrs.hoursLeft = 0
                                final = initial - hrs.hoursLeft
                                staffProjectSkill.objects.create(projectID= projectAdd, staffID=st,
                                                                 skillID=skills.objects.get(skillID=sk), hours=final,
                                                                 month=sMonth)
                                hrs.save()
                                dates.save()
                            else:
                                for month in range(sMonth, eMonth + 1):
                                    if dates.hoursRequired > 0:
                                        hrs = stSkill.get(month=month)
                                        initial = hrs.hoursLeft
                                        if hrs.hoursLeft >= dates.hoursRequired:
                                            hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                            dates.hoursRequired = 0
                                        else:
                                            dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                            hrs.hoursLeft = 0
                                        final = initial - hrs.hoursLeft
                                        staffProjectSkill.objects.create(projectID= projectAdd, staffID=st,
                                                                         skillID=skills.objects.get(skillID=sk),
                                                                         hours=final, month=month)
                                        hrs.save()
                                        dates.save()
                    except ObjectDoesNotExist:
                        messages.success(request, "Added but the staff member doesnt have one or many skills selected!")

                startDate = min(sDate)
                endDate = max(eDate)
                staffWithProjects.objects.create(projects_ID= projectAdd, profile_ID=profile.objects.get(staffID=staff[0]),
                                                 status="Working", startDate=startDate, endDate=endDate)
            alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                          project= projectAdd, info="added to")
            staffAlerts.objects.create(alertID=alert, staffID=profile.objects.get(staffID=staff[0]), status="Unseen")
            messages.success(request, "Staff added succesfully!")
            alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                          project= projectAdd, info="Added Staff to Project")
            staffAlerts.objects.create(alertID=alert, staffID=admin, status="Unseen")
            return projectprofile_View(request,  projectAdd.projectID)
        elif "reject" in request.POST:
            staffID = request.POST.getlist("reject")
            alertID = request.POST.getlist('seen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0]) & Q(staffID=query.staffID))
            alertObj.update(status="Seen")
            project = request.POST.getlist("projectNum")
            proj = projects.objects.get(projectID=project[0])
            alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                         project=proj,info="declined" )
            staff = profile.objects.get(staffID=staffID[0])
            staffAlerts.objects.create(alertID=alert, staffID=staff, status="Unseen")
            messages.success(request,
                             staff.user.first_name + " " + staff.user.last_name + "'s Request to join " +alert.project.projectName+" Declined")
            return projectprofile_View(request,project[0])
    return render(request,'alerts/alerts.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def requestproject_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = "Request Project"

    form = ProjectForm(request.POST or None)

    newID = projects.objects.values_list('projectID',flat=True)
    admin = profile.objects.get(staffID=1)
    if form.is_valid():
        project = form.save(commit=False)
        pm = request.POST.getlist('selectPM')
        project.projectManager= query
        project.status = "Pending Approval"
        project.save()
        proj = projects.objects.get(projectID=project.projectID)
        staffWithProjects.objects.create(projects_ID=proj, profile_ID=query,
                                         status="Working",startDate=proj.startDate,endDate=proj.endDate)
        alert = alerts.objects.create(fromStaff=query,alertType='Project',alertDate=datetime.date.today(),project=project)
        staffAlerts.objects.create(alertID=alert,staffID=admin,status="Unseen")
        messages.success(request, "Project requested succesfully!")
        return addpskill_View(request, max(newID))


    return render(request,'projects/requestproject.html',{"title":title,"form":form,"query":query})


@login_required
def addpskill_View(request, project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username
    admin = profile.objects.get(staffID = 1)
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = projects.objects.get(projectID=project_id)
    endDate = str(title.endDate.strftime('%Y-%m-%d'))
    startDate = str(title.startDate.strftime('%Y-%m-%d'))
    if title.projectManager != query:
        return render(request,'errorpermission.html')  # check if user is pm of that project


    skillset = skills.objects.exclude(projectID=project_id)

    if request.POST and ('continue' in request.POST or 'save' in request.POST):
        skill = request.POST.getlist('skillselec')
        hrs = request.POST.getlist('hours')
        start = request.POST.getlist('sdate')
        end = request.POST.getlist('edate')
        hrs = filter(lambda x: x != "", hrs)
        count = len(skill)
        x = 0
        while x < count:
            projectsWithSkills.objects.create(projectID_id=project_id, skillID_id=skill[x], hoursRequired=hrs[x],startDate=start[x],endDate=end[x])
            x = x + 1
        messages.success(request, "Skill added succesfully!")
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                      project=title, info="Added Skills to Project")
        staffAlerts.objects.create(alertID=alert, staffID=admin, status="Unseen")

        return projectprofile_View(request, project_id)

    return render(request, 'projects/addskill.html', {"title":title, "skillset":skillset,"startDate":startDate,"endDate":endDate})

@login_required
def addpstaff_View(request, project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username
    admin = profile.objects.get(staffID = 1)
    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')


    title = projects.objects.get(projectID=project_id)
    count = title.staffwithprojects_set.filter(status="Working").count()
    if title.projectManager != query:
        return render(request,'errorpermission.html') #check if user is pm of that project

    # exclude project managers and admins also staff which have holidays during the project
    list = profile.objects.exclude(projects=project_id).exclude(designation="Project Manager").exclude(designation="Admin").exclude(workStatus="Not Employeed")

    number = title.numberOfStaff - profile.objects.filter(projects=project_id).count()
    skill = title.projectswithskills_set.all()
    if request.POST and 'add' in request.POST:
        staff = request.POST.getlist('selectStaff')
        date = request.POST.getlist('selectDate')
        st = profile.objects.get(staffID=staff[0])
        if date == []:
            projSkills = title.projectswithskills_set.all()
            for sk in projSkills:
                dates = title.projectswithskills_set.get(skillID=sk.skillID_id)
                sMonth = dates.startDate.month
                eMonth = dates.endDate.month
                try:
                    if dates.hoursRequired > 0:
                        stSkill = st.staffwithskills_set.filter(skillID=sk.skillID)
                        if sMonth is eMonth:
                            hrs = stSkill.get(month=sMonth)
                            initial = hrs.hoursLeft
                            if hrs.hoursLeft >= dates.hoursRequired:
                                hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                dates.hoursRequired = 0
                            else:
                                dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                hrs.hoursLeft = 0
                            final = initial - hrs.hoursLeft
                            staffProjectSkill.objects.create(projectID=title, staffID=st,
                                                             skillID=skills.objects.get(skillID=sk.skillID_id),
                                                             hours=final,
                                                             month=sMonth)
                            hrs.save()
                            dates.save()
                        else:
                            for month in range(sMonth, eMonth + 1):
                                if dates.hoursRequired > 0:
                                    hrs = stSkill.get(month=month)
                                    initial = hrs.hoursLeft
                                    if hrs.hoursLeft >= dates.hoursRequired:
                                        hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                        dates.hoursRequired = 0
                                    else:
                                        dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                        hrs.hoursLeft = 0
                                    final = initial - hrs.hoursLeft
                                    staffProjectSkill.objects.create(projectID=title, staffID=st,
                                                                     skillID=skills.objects.get(skillID=sk.skillID_id),
                                                                     hours=final, month=month)
                                    hrs.save()
                                    dates.save()

                except ObjectDoesNotExist:
                    None

            staffWithProjects.objects.create(projects_ID=title, profile_ID=profile.objects.get(staffID=staff[0]),
                                             status="Working", startDate=title.startDate, endDate=title.endDate)
        else:
            sDate = []
            eDate = []
            for sk in date:
                dates = title.projectswithskills_set.get(skillID=sk)
                sDate.append(dates.startDate)
                eDate.append(dates.endDate)
                sMonth = dates.startDate.month
                eMonth = dates.endDate.month

                try:
                    if dates.hoursRequired > 0:
                        stSkill = st.staffwithskills_set.filter(skillID=sk)
                        if sMonth is eMonth:
                            hrs = stSkill.get(month=sMonth)
                            initial = hrs.hoursLeft
                            if hrs.hoursLeft >= dates.hoursRequired:
                                hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                dates.hoursRequired = 0
                            else:
                                dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                hrs.hoursLeft = 0
                            final = initial - hrs.hoursLeft
                            staffProjectSkill.objects.create(projectID=title, staffID=st,
                                                             skillID=skills.objects.get(skillID=sk), hours=final,month=sMonth)
                            hrs.save()
                            dates.save()
                        else:
                            for month in range(sMonth,eMonth+1):
                                if dates.hoursRequired > 0:
                                    hrs = stSkill.get(month = month)
                                    initial = hrs.hoursLeft
                                    if hrs.hoursLeft >= dates.hoursRequired:
                                        hrs.hoursLeft = hrs.hoursLeft - dates.hoursRequired
                                        dates.hoursRequired = 0
                                    else:
                                        dates.hoursRequired = dates.hoursRequired - hrs.hoursLeft
                                        hrs.hoursLeft = 0
                                    final = initial - hrs.hoursLeft
                                    staffProjectSkill.objects.create(projectID=title, staffID=st,
                                                                         skillID=skills.objects.get(skillID=sk),
                                                                         hours=final, month=month)
                                    hrs.save()
                                    dates.save()
                except ObjectDoesNotExist:
                    messages.success(request, "Added but the staff member doesnt have one or many skills selected!")

            startDate = min(sDate)
            endDate = max(eDate)
            staffWithProjects.objects.create(projects_ID=title, profile_ID=profile.objects.get(staffID=staff[0]),
                                             status="Working", startDate=startDate, endDate=endDate)
        alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                      project=title,info="added to")
        staffAlerts.objects.create(alertID=alert, staffID=profile.objects.get(staffID=staff[0]), status="Unseen")
        messages.success(request, "Staff added succesfully!")
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                      project=title, info="Added Staff to Project")
        staffAlerts.objects.create(alertID=alert, staffID=admin, status="Unseen")
        return projectprofile_View(request,title.projectID)


    return render(request, 'projects/addstaff.html',{"title":title,"list":list,"number":number,"skill":skill,"count":count})

@login_required
def holiday_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = "Request Leave"


    admin = profile.objects.get(staffID=1)
    if request.method == "POST":
        form = HolidaysForm(request.POST, user=request.user)
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
    return render(request, 'profile/requestholiday.html', {"title":title, "form":form})

@login_required
def requests_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')

    title = "My Requests"


    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)

    return render(request,'employee/requests.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def matchmakingSelect_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return render(request,'errorpermission.html')

    title = "Matchmaking"
    allProjects = projects.objects.filter(projectManager=query)

    return render(request, 'projects/matchmaking.html', {"title": title,"allProjects":allProjects})


@login_required
def matchmaking_View(request,project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return render(request,'errorpermission.html')

    title = "Matchmaking"
    allProjects =  projects.objects.filter(projectManager=query)
    project = projects.objects.get(projectID=project_id)


    if query != project.projectManager:
        return render(request, 'errorpermission.html')

    # exlude PMS and Admins
    staffList = profile.objects.filter(Q(designation="Employee") | Q(designation="Contractor")| Q(designation="Project Manager"))
    # exclude already in project
    staffList = staffList.exclude(workStatus="Not Employeed")
    staffList = staffList.exclude(projects__projectID__exact=project.projectID)
    # holidays during the project
    months = project.endDate.month - project.startDate.month
    if(months<0):
        months = months + 12
    if months == 0:
        months =1
    full = []
    fsome = []
    partial = []
    some = []
    #match skills
    fullCount = 0
    count = 0
    all = 0
    somem = 0
    dict = {}
    continueFor = False
    holidayID = []
    for staff in staffList:
        totalSkills = project.projectswithskills_set.count()
        for projSkill in project.projectswithskills_set.all():
            if projSkill.hoursRequired > 0:
                sMonth = projSkill.startDate.month
                eMonth = projSkill.endDate.month
                sDate = projSkill.startDate
                eDate = projSkill.endDate
                if sMonth == eMonth:
                    try:
                        hrs = staff.staffwithskills_set.get(Q(skillID=projSkill.skillID)&Q(month=sMonth))
                        if hrs.hoursLeft > projSkill.hoursRequired:
                            fullCount = fullCount +1
                            count = count +1
                        else:
                            count = count + 1
                    except ObjectDoesNotExist:
                        None
                else:
                    required = projSkill.hoursRequired
                    for month in range(sMonth,eMonth+1):
                        try:
                            hrs = staff.staffwithskills_set.get(Q(skillID=projSkill.skillID) & Q(month=month))
                            try:
                                hol = staff.holidays_set.filter(Q(startDate__gte=sDate)&Q(endDate__lte=eDate))
                                for holiday in hol:
                                    for mon in range(holiday.startDate.month,holiday.endDate.month+1):
                                        if mon is month:
                                            continueFor = True
                                            holidayID.append(holiday.holidayID)
                            except ObjectDoesNotExist:
                                None

                            if continueFor is True:
                                continueFor = False
                                continue
                            if hrs.hoursLeft >= required:
                                all = 1
                                somem = 0
                                break
                            elif hrs.hoursLeft < required and hrs.hoursLeft is not 0:
                                required = required - hrs.hoursLeft
                                somem = 1
                        except ObjectDoesNotExist:
                                somem = 0
                                all = 0
                    if all is 1:
                        fullCount =fullCount+1
                        count = count + 1
                    elif somem is 1:
                        count = count +1
        if totalSkills is not 0 and count is not 0:
            if fullCount is totalSkills:
                full.append(staff)
            elif count is totalSkills and fullCount is not totalSkills and fullCount is not 0:
                fsome.append(staff)
            elif count is totalSkills and fullCount is 0:
                partial.append(staff)
            elif count is not 0:
                some.append(staff)
        skillids = staff.staffwithskills_set.values_list('skillID', flat=True)
        skillNames = []
        skillids = list(set(skillids))
        for id in skillids:
            skillnamepresent =skills.objects.get(skillID=id)
            skillNames.append(skillnamepresent.skillName)
        finalSkills = []
        for name in project.projectswithskills_set.all():
            if name.skillID.skillName in skillNames and name.hoursRequired > 0:
                finalSkills.append(name.skillID.skillName)
        dict.update({staff.staffID: finalSkills})
        count = 0
        fullCount = 0
     #adding staff

    startDate = []
    endDate = []
    dates = project.projectswithskills_set.all()
    if request.POST:
        staffID = request.POST.getlist("selectStaff")
        staff = profile.objects.get(staffID=staffID[0])
        for sk in dates:
            for sSkill in staff.staffwithskills_set.all():
                if sk.skillID_id == sSkill.skillID_id:
                    startDate.append(sk.startDate)
                    endDate.append(sk.endDate)
            sMonth = sk.startDate.month
            eMonth = sk.endDate.month
            stSkill = staff.staffwithskills_set.filter(skillID=sk.skillID)
            try:
                for month in range(sMonth,eMonth+1):
                    if sk.hoursRequired > 0:
                        hrs = stSkill.get(month=month)
                        initial = hrs.hoursLeft
                        if hrs.hoursLeft >=sk.hoursRequired:
                            hrs.hoursLeft = hrs.hoursLeft - sk.hoursRequired
                            sk.hoursRequired = 0
                        else:
                            sk.hoursRequired = sk.hoursRequired - hrs.hoursLeft
                            hrs.hoursLeft = 0
                        final = initial - hrs.hoursLeft
                        staffProjectSkill.objects.create(projectID=project, staffID=staff,skillID=skills.objects.get(skillID=sk.skillID_id),hours=final, month=month)
                        hrs.save()
                        sk.save()
            except:
                None

        start = min(startDate)
        end = max(endDate)
        staffWithProjects.objects.create(projects_ID=project, profile_ID=staff,
                                         status="Working", startDate=start, endDate=end)

        alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                      project=project, info="added to")
        staffAlerts.objects.create(alertID=alert, staffID=staff, status="Unseen")
        messages.success(request, "Staff added succesfully!")

    return render(request,'projects/matchmaking.html',{"title":title,"allProjects":allProjects,"full":full,"fsome":fsome,"partial":partial,"some":some,"project":project,"holidayID":holidayID,"dict":dict})


@login_required
def messageBoard_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return render(request,'errorpermission.html')

    title = "Message Board"
    allProjects = projects.objects.filter(staffID=query.staffID)
    allBoards = []
    for proj in allProjects:
        try:
            board = messageBoard.objects.get(projectID=proj.projectID)
            allBoards.append(board)
        except:
            None

    return render(request, 'projects/message.html', {"title": title,"allBoards":allBoards})

@login_required
def comments_View(request,board_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return render(request,'errorpermission.html')

    board = messageBoard.objects.get(boardID=board_id)
    comments = boardComments.objects.filter(board_id=board_id)
    title = board.projectID.projectName+"'s Message Board"
    found = False
    project = projects.objects.get(projectID=board.projectID.projectID)
    for staff in project.staffwithprojects_set.all():
        if query.staffID == staff.profile_ID.staffID:
            found=True
    if found is False:
        return render(request, 'errorpermission.html')

    if request.POST:
        comment = request.POST.getlist("comment")
        boardComments.objects.create(board=board,staff=query,comment=comment[0],time=datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))
        messages.success(request, "Comment Posted Succesfully")

    return render(request, 'projects/comments.html', {"title": title,"comments":comments,"board":board})

@login_required
def comments_Box(request,board_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return render(request,'errorpermission.html')

    board = messageBoard.objects.get(boardID=board_id)
    comments = boardComments.objects.filter(board_id=board_id)
    title = board.projectID.projectName + "'s Message Board"
    found = False
    project = projects.objects.get(projectID=board.projectID.projectID)
    for staff in project.staffwithprojects_set.all():
        if query.staffID == staff.profile_ID.staffID:
            found = True
    if found is False:
        return render(request, 'errorpermission.html')

    return render(request, 'projects/commentBox.html', {"comments":comments,"board":board})

@login_required
def report_View(request,project_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username

    if query.designation != "Project Manager":  # check if admin
        return render(request,'errorpermission.html')
    # Create the HttpResponse object with the appropriate PDF headers.
    query = projects.objects.get(projectID=project_id)

    if query.projectManager != profile.objects.get(user=username):
        return render(request, 'errorpermission.html')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Report.pdf"'


    # Create the PDF ob ject, using the response object as its "file."
    p = canvas.Canvas(response)
    fn = os.path.join(settings.BASE_DIR, 'adminUser/static/img/leidos_logo_2013.jpg')
    p.drawImage(fn,0,782,width=600,height=60)


    p.drawString(210, 750, "Project Report")
    # p.showPage()



    p.drawString(20, 710, "Project ID: "+str(query.projectID))
    p.drawString(20, 690, "Project Name: "+query.projectName+"    Status: "+query.status)
    p.drawString(20, 670, "Project Type: " + query.type)
    p.drawString(20, 650, "Description: " + query.description)
    p.drawString(20, 600, "Start Date: " + str(query.startDate) + "     End Date: " + str(query.endDate))
    p.drawString(20,580,"Country: "+query.location.country+"    City: "+query.location.city )
    p.drawString(200, 540, "Project Manager: "+query.projectManager.user.first_name+" "+query.projectManager.user.last_name)
    p.drawString(20,520,"Projet Manager Skill Level: "+str(query.projectManager.skillLevel))
    p.drawString(20,500,"Project Manager Staff ID: "+str(query.projectManager.staffID))
    p.drawString(20,480,"Project Manager Skills: ")
    x = 460
    i = 1
    skillids = query.projectManager.staffwithskills_set.values_list('skillID', flat=True)
    skillNames = []
    skillids = list(set(skillids))
    for id in skillids:
        skillNames.append(skills.objects.get(skillID=id))

    for skill in skillNames:
        p.drawString(140,x,str(i)+") "+skill.skillName)
        x = x - 20
        i = i + 1
    p.showPage()
    d = Drawing(300, 300)
    bar = VerticalBarChart()
    bar.x = 100
    bar.y = 85
    bar.valueAxis._valueMin=0
    bar.valueAxis._valueMax=100
    skillLevel = []
    staffList = query.staffwithprojects_set.filter(status="Working")
    for staff in staffList:
        skillLevel.append(staff.profile_ID.skillLevel)

    data = [skillLevel
            ]
    print data
    bar.data = data
    bar.categoryAxis.categoryNames = []

    for staff in staffList:
        bar.categoryAxis.categoryNames.append(staff.profile_ID.user.last_name)

    bar.bars[0].fillColor = PCMYKColor(0, 100, 100, 40, alpha=85)
    bar.bars[1].fillColor = PCMYKColor(23, 51, 0, 4, alpha=85)
    bar.bars.fillColor = PCMYKColor(100, 0, 90, 50, alpha=85)

    d.add(bar, '')
    p.drawImage(fn, 0, 782, width=600, height=60)
    p.drawString(210, 750, "Statistics")
    p.drawString(10, 730, "This graph shows different skill levels of the employees working on this project.")
    d.drawOn(p, 10, 500)

    d = Drawing()
    pie = Pie()
    pie.x = 200
    pie.y = 65
    pm = staffList.filter(profile_ID__designation="Project Manager").count()
    emp = staffList.filter(profile_ID__designation="Employee").count()
    cont = staffList.filter(profile_ID__designation="Contractor").count()

    total = staffList.count()

    pm = float(pm) / float(total) * 100
    emp = float(emp) / float(total) * 100
    cont = float(cont) / float(total) * 100

    pie.data = [pm, emp, cont]
    pie.labels = ["Project Manager " +str(round(pm,2)) + "%", "Employee " + str(round(emp,2)) + "%", "Contractor: " + str(round(cont,2)) + "%", ]
    pie.slices.strokeWidth = 0.5
    p.drawString(10, 530, "This graph shows different percantage of employee types working on this project")
    d.add(pie)
    d.drawOn(p, 10, 300)
    p.showPage()
    p.drawImage(fn, 0, 782, width=600, height=60)

    p.drawString(140, 750, "Staff Working on Project")

    x = 710
    for staff in query.staffID.all():
        p.drawString(20,x,"Staff ID: "+str(staff.staffID)+"     Name: "+staff.user.first_name+" "+" "+staff.user.last_name)
        x = x - 20
    p.showPage()
    p.drawImage(fn, 0, 782, width=600, height=60)

    p.drawString(160, 750, "Skills for the Project")
    x = 710
    i = 1

    for skill in query.skills_set.all():
        p.drawString(20,x,str(i)+") "+skill.skillName)
        x = x - 20
        i = i + 1

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response