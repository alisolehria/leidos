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


@login_required
def alerttab_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if project Manager
        return HttpResponse(status=201)
    title = "Alerts"
    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by('-alertID')


    return render(request, 'alerts/alertTab.html', {"title":title, "alertList":alertList})

@login_required
def profile_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if project Manager
        return HttpResponse(status=201)

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
        return HttpResponse(status=201)
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
        return HttpResponse(status=201)
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
        return HttpResponse(status=201)
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
        return HttpResponse(status=201)

    title = "Projects List"
    list = projects.objects.all() #get all the objects from profile table
    return render(request,'projects/projectlist.html',{"list":list,"title":title})

@login_required()
def projectprofile_View(request, project_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Project Manager":  # check if admin
        return HttpResponse(status=201)

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
        return HttpResponse(status=201)
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
        return HttpResponse(status=201)


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
        return HttpResponse(status=201)

    title = "Alerts"


    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)

    if request.POST:
        if "unseen" in request.POST:
            alertID = request.POST.getlist('unseen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0])&Q(staffID=query.staffID))
            alertObj.update(status="Seen")
        elif "accept" in request.POST:
            staffID = request.POST.getlist("accept")
            alertID = request.POST.getlist('seen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0]) & Q(staffID=query.staffID))

            project = request.POST.getlist("projectNum")
            staff = profile.objects.get(staffID=staffID[0])
            proj = projects.objects.get(projectID=project[0])
            alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                          project=proj)
            staffWithProjects.objects.create(projects_ID=proj, profile_ID=staff,
                                             status="Working", startDate=proj.startDate, endDate=proj.endDate)
            alertObj.update(status="Seen")
            staffAlerts.objects.create(alertID=alert, staffID=staff, status="Unseen")
            messages.success(request,staff.user.first_name+" "+staff.user.last_name+" Added Succesfully to "+alert.project.projectName )
            return projectprofile_View(request,project[0])
        elif "reject" in request.POST:
            staffID = request.POST.getlist("reject")
            alertID = request.POST.getlist('seen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0]) & Q(staffID=query.staffID))
            alertObj.update(status="Seen")
            project = request.POST.getlist("projectNum")
            proj = projects.objects.get(projectID=project[0])
            alert = alerts.objects.create(fromStaff=query, alertType='Project Request', alertDate=datetime.date.today(),
                                         project=proj )
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
        return HttpResponse(status=201)

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
        return HttpResponse(status=201)

    title = projects.objects.get(projectID=project_id)
    endDate = str(title.endDate.strftime('%Y-%m-%d'))
    startDate = str(title.startDate.strftime('%Y-%m-%d'))
    if title.projectManager != query:
        return HttpResponse(status=201)  # check if user is pm of that project


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
        return HttpResponse(status=201)


    title = projects.objects.get(projectID=project_id)
    count = title.staffwithprojects_set.filter(status="Working").count()
    if title.projectManager != query:
        return HttpResponse(status=201) #check if user is pm of that project

    # exclude project managers and admins also staff which have holidays during the project
    list = profile.objects.exclude(projects=project_id).exclude(designation="Project Manager").exclude(designation="Admin").exclude(workStatus="Not Employeed")

    number = title.numberOfStaff - profile.objects.filter(projects=project_id).count()
    skill = title.projectswithskills_set.all()
    if request.POST and 'add' in request.POST:
        staff = request.POST.getlist('selectStaff')
        date = request.POST.getlist('selectDate')
        st = profile.objects.get(staffID=staff[0])
        if date == []:
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
        return HttpResponse(status=201)

    title = "Request Leave"

    form = HolidaysForm(request.POST or None)
    admin = profile.objects.get(staffID=1)
    if form.is_valid() and request.POST:
        hol = form.save(commit=False)
        hol.status="Pending Approval"
        hol.staffID_id = query.staffID
        hol.save()
        alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                      holiday=hol, info="Your Project Request")
        staffAlerts.objects.create(alertID=alert, staffID=admin, status="Unseen")
        messages.success(request, "Leave Requested!")

    return render(request, 'profile/requestholiday.html', {"title":title, "form":form})

@login_required
def requests_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if admin
        return HttpResponse(status=201)

    title = "My Requests"


    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)

    return render(request,'employee/requests.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def matchmakingSelect_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return HttpResponse(status=201)

    title = "Matchmaking"
    allProjects = projects.objects.filter(projectManager=query)

    return render(request, 'projects/matchmaking.html', {"title": title,"allProjects":allProjects})


@login_required
def matchmaking_View(request,project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return HttpResponse(status=201)

    title = "Matchmaking"
    allProjects =  projects.objects.filter(projectManager=query)
    project = projects.objects.get(projectID=project_id)
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
    continueFor = False
    holidayID = []
    for staff in staffList:
        totalSkills = project.projectswithskills_set.count()
        for projSkill in project.projectswithskills_set.all():
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
                        # staffProjectSkill.objects.create(projectID=project, staffID=staff,
                        #                                  skillID=skills.objects.get(skillID=sk.skillID_id),
                        #                                  hours=final, month=month)
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

    return render(request,'projects/matchmaking.html',{"title":title,"allProjects":allProjects,"full":full,"fsome":fsome,"partial":partial,"some":some,"project":project,"holidayID":holidayID})


@login_required
def messageBoard_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
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

    return render(request, 'projects/message.html', {"title": title,"allBoards":allBoards})

@login_required
def comments_View(request,board_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Project Manager":  # check if pm
        return HttpResponse(status=201)

    board = messageBoard.objects.get(boardID=board_id)
    comments = boardComments.objects.filter(board_id=board_id)
    title = board.projectID.projectName+"'s Message Board"

    if request.POST:
        comment = request.POST.getlist("comment")
        boardComments.objects.create(board=board,staff=query,comment=comment[0],time=datetime.date.today())
        messages.success(request, "Comment Posted Succesfully")

    return render(request, 'projects/comments.html', {"title": title,"comments":comments,"board":board})