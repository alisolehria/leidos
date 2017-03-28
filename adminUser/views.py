from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import profile, projects, skills, staffWithSkills, projectsWithSkills, holidays, alerts, staffAlerts, staffWithProjects, staffProjectSkill, messageBoard, boardComments
from .models import location
from django.http import HttpResponse
import datetime
from django.contrib.auth.models import User
from .forms import UserForm,UserProfileForm,ProjectForm, SkillForm, LocationForm, UserUpdateForm, HolidaysForm
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from reportlab.pdfgen import canvas
import os.path
from django.core.exceptions import ObjectDoesNotExist
from reportlab.lib.colors import PCMYKColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie




@login_required
def dashboard_View(request):
    username = request.user
    query = profile.objects.get(user=username)
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    num = profile.objects.exclude(workStatus="Not Employeed").count() #get number of staff
    projectNum = projects.objects.filter(status='On Going').count()#number of active projects


    time = datetime.date.today() #get todays date
    upcoming = projects.objects.filter(status="Approved") #check if greater than todays date

    return render(request, 'profile/dashboard.html',{"title":username,"info":query,'num':num,'projectNum':projectNum,'upcoming':upcoming,"time":time})

@login_required()
def stafflist_View(request):
    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    list = profile.objects.all() #get all the objects from profile table
    title = "Staff List"
    if request.POST:
        staffList = request.POST.getlist('selectStaff')
        for staff in staffList:
             return staffprofile_View(request,staff)

    return render(request,'staff/stafflist.html',{"list":list,"title":title})

@login_required()
def projectlist_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Projects List"
    list = projects.objects.all() #get all the objects from profile table

    return render(request,'project/projectlist.html',{"list":list,"title":title})

@login_required()
def currentstaff_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')


    list = projects.objects.filter(status="Completed") ##get all the objects from profile table exclueding not employeed
    title = "Completed Projects"
    return render(request,'project/projectlist.html',{"list":list,"title":title})

@login_required()
def currentprojects_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "On Going Projects"
    list = projects.objects.filter(status="On Going") #get only projects which are ongoing
    return render(request,'project/projectlist.html',{"list":list,"title":title})

@login_required()
def upcomingprojects_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Upcoming Projects"
    list = projects.objects.filter(status="Approved")  #get only projects which are approved
    return render(request,'project/projectlist.html',{"list":list,"title":title})


@login_required()
def staffprofile_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')


    info = profile.objects.get(staffID = staff_id)
    title = info.user.first_name+" "+info.user.last_name
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
    month =  datetime.datetime.now().strftime("%m")
    nextMonth = int(month) + 1
    nNextMonth = int(month) + 2

    month = month.lstrip('0')
    nextMonth = str(nextMonth).lstrip('0')
    nNextMonth = str(nNextMonth).lstrip('0')


    skillList = skillhrs.filter(Q(month=nextMonth)|Q(month=month)|Q(month=nNextMonth))

    hrsAvailable = 0
    hrsLeft = 0
    for sk in skillList:
        hrsAvailable = hrsAvailable + sk.hoursAvailable
        hrsLeft = hrsLeft + sk.hoursLeft

    try:
        percentage = float(hrsLeft)/float(hrsAvailable) * 100
    except ZeroDivisionError:
        percentage = 100


    if request.POST and "remove" in request.POST:
        id = request.POST.getlist("remove")
        projs = info.staffwithprojects_set.all()
        for project in projs:
            project.status="Not Working"
            project.save()
        info.workStatus="Not Employeed"
        info.user.is_active=0
        info.save()
        info.user.save()
        messages.success(request, "Employee Blocked")

    return render(request,'staff/staffprofile.html',{"info":info,"title":title,"ongoing":ongoing,"upcoming":upcoming,"completed":completed,"skillhrs":skillhrs,"skillNames":skillNames,"percentage":percentage})

@login_required()
def currentprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    #get ongoing project of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "On Going Projects of " + info.user.first_name + " " + info.user.last_name
    list =  info.staffwithprojects_set.filter(Q(startDate__lte=time) & Q(endDate__gte=time) & Q(status="Working"))
    return render(request,'staff/projectlist.html',{"list":list,"title":title})

@login_required()
def upcomingprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    #upcoming projects of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "Upcoming Projects of " + info.user.first_name + " " + info.user.last_name
    list = info.staffwithprojects_set.filter(Q(startDate__gt=time) & Q(status="Working"))
    return render(request,'staff/projectlist.html',{"list":list,"title":title})

@login_required()
def completedprojectsget_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    #completed projects of specific user
    time = datetime.date.today()
    info = profile.objects.get(staffID=staff_id)
    title = "Completed Projects of " + info.user.first_name + " " + info.user.last_name
    list = info.staffwithprojects_set.filter(Q(endDate__lt=time) & Q(status="Working"))
    return render(request,'staff/projectlist.html',{"list":list,"title":title})

@login_required()
def projectprofile_View(request, project_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
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

    skillhrset = []
    skillhrs = info.projectswithskills_set.all()
    skillhrset = list(skillhrs)

    skillwithhrs = {}
    current = staffWithProjects.objects.filter(projects_ID=project_id)
    current = current.exclude(status="Not Working")
    i = 0
    while i < len(skillset):
        skillwithhrs.update({skillset[i]: skillhrset[i]})
        i = i + 1



    if request.POST:
        if "decline" in request.POST:
            id = request.POST.getlist("decline")
            project = projects.objects.filter(projectID=id[0])
            project.update(status="Declined")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info,info="Your Project Request")
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info) & Q(fromStaff=info.projectManager.staffID))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Project Status Changed")
            return projectlist_View(request)
        elif "accept" in request.POST:
            id = request.POST.getlist("accept")
            project = projects.objects.filter(projectID=id[0])
            project.update(status="Approved")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info,info="Your Project Request")
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info)&Q(fromStaff=info.projectManager.staffID))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Project Status Changed")
            return projectlist_View(request)
        elif "discontinue" in request.POST:
            id = request.POST.getlist("discontinue")
            project = projects.objects.filter(projectID=id[0])
            info = projects.objects.get(projectID=id[0])
            project.update(status="Discontinued")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info,info="Project")
            working = info.staffID.all()
            for staff in working:
                employee = profile.objects.get(staffID=staff.staffID)
                staffAlerts.objects.create(alertID=alert, staffID=employee, status="Unseen")
            messages.success(request, "Project Status Changed")
            return projectlist_View(request)
        elif "remove" in request.POST:
            id = request.POST.getlist("remove")
            proj = staffWithProjects.objects.filter(profile_ID=id[0])
            st = profile.objects.get(staffID=id[0])
            proj = proj.filter(projects_ID=project_id)
            proj.update(status="Not Working")
            try:
                skill = staffProjectSkill.objects.filter(Q(projectID_id=info.projectID)&Q(staffID_id=st))
                for sk in skill:
                    pskill = info.projectswithskills_set.get(skillID=sk.skillID)
                    final = pskill.hoursRequired + sk.hours
                    pskill.hoursRequired=final
                    sskill = st.staffwithskills_set.get(Q(skillID=sk.skillID)&Q(month=sk.month))
                    final = sskill.hoursLeft + sk.hours
                    sskill.hoursLeft=final
                    pskill.save()
                    sskill.save()
            except ObjectDoesNotExist:
                messages.success(request, "No effect to one or many skills")

            alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                          project=info,info="removed from")
            staffAlerts.objects.create(alertID=alert, staffID=profile.objects.get(staffID=id[0]), status="Unseen",
                                       )
            messages.success(request, "Staff Removed")

    return render(request,'project/projectprofile.html',{"title":title,"info":info,"skillwithhrs":skillwithhrs,"past":past,"current":current,"count":count})

@login_required
def table_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    # auto refresh view
    num = projects.objects.filter(status="Completed").count() #get number of staff
    projectNum = projects.objects.filter(status='On Going').count()#number of active projects


    today = datetime.date.today() #get todays date
    upcoming = projects.objects.filter(status="Approved") #check if greater than todays date

    return render(request, 'profile/table.html',{"info":query,'num':num,'projectNum':projectNum,'upcoming':upcoming})

@login_required()
def addstaff_View(request):

    username = request.user
    query = profile.objects.get(user=username)  # get username
    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Add Staff"


    #this is adding to tables
    if request.method=="POST":
        form = UserForm(request.POST)
        form2 = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            user_query = profile.objects.values_list('staffID',flat=True)
            firstletter = str(firstname[0])
            secondletter = str(lastname[0])
            new_password = "leidos123"
            new_username = str.lower(firstletter) + str.lower(secondletter) + (str(max(user_query)+1)) #take first letters of fname and lname along with staff id to generate username
            emailToSend = [form.cleaned_data.get('email')]
            #send_mail('Welcome To Leidos','Your account has been created. Following are your account credentials.\n\n Username= '+new_username+'\n Password: leidos123\n\n\nThank You.','leidos.syntax@gmail.com',emailToSend,fail_silently=False,)
            user= form.save(commit=False)
            user.username = new_username
            user.set_password(new_password)
            user.save()
            userprofile = form2.save(commit=False)
            userprofile.user= user;
            userprofile.workStatus="Working"
            userprofile.skillLevel="0"
            if userprofile.designation == "Admin":
                userprofile.salary=15000
            elif userprofile.designation == "Project Manager":
                userprofile.salary = 10000
            elif userprofile.designation == "Contractor":
                userprofile.salary = 5000
            else:
                userprofile.salary = 8000

            userprofile.save()
            messages.success(request, firstname+" "+lastname+"'s account created successfully!")
            return addskill_View(request,max(user_query)+1)
    else:
        form = UserForm()
        form2 = UserProfileForm()

    return render(request,'staff/addstaff.html',{"title":title,"form":form,"form2":form2})


@login_required
def addskill_View(request, staff_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    user = profile.objects.get(staffID=staff_id)
    title = user.user.first_name + " " + user.user.last_name

    high = skills.objects.filter(priority="High").count();
    mid = skills.objects.filter(priority="Mid").count();
    low = skills.objects.filter(priority="Low").count();



    skillset = skills.objects.exclude(staffID=staff_id)

    if(request.POST and "submitskill" in request.POST):
        skill = request.POST.getlist('skillselec')
        hrs = request.POST.getlist('hours')
        hrs= filter(lambda x: x != "", hrs)
        count = len(skill)

        x = 0
        month = 1
        while x < count:
            for month in range(1,13):
                staffWithSkills.objects.create(staffID_id=staff_id,skillID_id=skill[x],hoursAvailable=hrs[x],hoursLeft=hrs[x],month=month,year=2017)
            x = x + 1
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Staff', alertDate=datetime.date.today(),
                                      info="Skill added to your profile")
        staffAlerts.objects.create(alertID=alert, staffID=user, status="Unseen")

        skillids = user.staffwithskills_set.values_list('skillID', flat=True)

        skillids = list(set(skillids))
        highpriority = 0
        midpriority = 0
        lowpriority = 0
        for id in skillids:
            sk = skills.objects.get(skillID=id)
            if sk.priority == "High":
                highpriority = highpriority + 1
            elif sk.priority == "Mid":
                midpriority = midpriority + 1
            else:
                lowpriority = lowpriority + 1
        higPercentage = float(highpriority) / float(high) * 50
        midPercentage = float(midpriority) / float(mid) * 30
        lowPercentage = float(lowpriority) / float(low) * 20
        sumSkills = higPercentage + midPercentage + lowPercentage
        user.skillLevel=sumSkills
        user.save()
        messages.success(request, "Skill added succesfully!")
        return staffprofile_View(request, staff_id)

    return render(request, 'staff/addskill.html', {"title":title, "skillset":skillset, "user":user})

@login_required
def addproject_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Add Project"
    pms = profile.objects.filter(designation="Project Manager")
    form = ProjectForm(request.POST or None)

    newID = projects.objects.values_list('projectID',flat=True)
    #testing
    if form.is_valid() and request.POST:
        project = form.save(commit=False)
        pm = request.POST.getlist('selectPM')
        pmquery = profile.objects.get(staffID=pm[0])
        project.projectManager= pmquery
        project.status = "Approved"
        project.save()
        proj = projects.objects.get(projectID=project.projectID)
        staffWithProjects.objects.create(projects_ID=proj, profile_ID=pmquery,
                                         status="Working",startDate=proj.startDate,endDate=proj.endDate)
        pm = profile.objects.get(staffID = pm[0])
        alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                      project=project)
        staffAlerts.objects.create(alertID=alert, staffID=pm, status="Unseen")
        msg = messageBoard.objects.create(projectID=project)
        boardComments.objects.create(board=msg,staff=query,comment="Welcome to the Message Board!",time=datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))
        messages.success(request, "Project added succesfully!")
        return addpskill_View(request,max(newID))


    return render(request,'project/addproject.html',{"title":title,"form":form,"pms":pms})




@login_required
def addpskill_View(request, project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = projects.objects.get(projectID=project_id)
    skillset = skills.objects.exclude(projectID=project_id)
    endDate=str(title.endDate.strftime('%Y-%m-%d'))
    startDate=str(title.startDate.strftime('%Y-%m-%d'))
    if request.POST and ('continue' in request.POST or 'save' in request.POST):
        skill = request.POST.getlist('skillselec')
        hrs = request.POST.getlist('hours')
        start = request.POST.getlist('sdate')
        end = request.POST.getlist('edate')
        hrs = filter(lambda x: x != "", hrs)
        count = len(skill)
        x = 0

        while x < count:

            projectsWithSkills.objects.create(projectID_id=project_id, skillID_id=skill[x], hoursRequired=hrs[x], startDate=start[x],endDate=end[x])
            x = x + 1

        messages.success(request, "Skill added succesfully!")
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                      project=title,info="Added Skills to Project" )
        staffAlerts.objects.create(alertID=alert, staffID=title.projectManager, status="Unseen")
        if 'continue' in request.POST:
            return addpstaff_View(request, project_id)
        elif 'save' in request.POST:
            return projectprofile_View(request, project_id)
        elif 'match' in request.POST:
            return matchmakingSelect_View(request,project_id)

    return render(request, 'project/addskill.html',{"title":title,"skillset":skillset,"startDate":startDate,"endDate":endDate})


@login_required
def addpstaff_View(request, project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = projects.objects.get(projectID=project_id)
    count = title.staffwithprojects_set.filter(status="Working").count()
    # exclude project managers and admins also staff which have holidays during the project
    list = profile.objects.exclude(projects=project_id).exclude(designation="Admin").exclude(workStatus="Not Employeed")

    number = title.numberOfStaff - profile.objects.filter(projects=project_id).count()
    skill = title.projectswithskills_set.all()
    message = "Added Successfully"
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
                                                             skillID=skills.objects.get(skillID=sk.skillID_id), hours=final,
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
                                             status="Working",startDate=title.startDate,endDate=title.endDate)
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
                    None

            startDate = min(sDate)
            endDate = max(eDate)
            staffWithProjects.objects.create(projects_ID=title, profile_ID=profile.objects.get(staffID=staff[0]),
                                             status="Working",startDate = startDate,endDate = endDate)
        alert = alerts.objects.create(fromStaff=query, alertType='Staff', alertDate=datetime.date.today(),
                                      project=title,info="added to")
        staffAlerts.objects.create(alertID=alert, staffID=profile.objects.get(staffID=staff[0]), status="Unseen")
        messages.success(request, "Staff added succesfully!")
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                      project=title, info="Added Staff to Project")
        staffAlerts.objects.create(alertID=alert, staffID=title.projectManager, status="Unseen")
        return projectprofile_View(request,title.projectID)

    return render(request, 'project/addstaff.html',{"title":title,"list":list,"number":number,"skill":skill,"count":count})

@login_required
def skill_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Add Skill"
    list = skills.objects.all()
    form = SkillForm(request.POST or None)

    if form.is_valid() and request.POST:
        skill = form.save(commit=False)
        skill.save()
        messages.success(request, "Skill added succesfully to the system!")

    return render(request, 'common/skill.html',{"title":title,"list":list,"form":form})

@login_required
def location_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Add Location"
    list = location.objects.all()
    form = LocationForm(request.POST or None)

    if form.is_valid() and request.POST:
        loc = form.save(commit=False)
        loc.save()
        messages.success(request, "Location added succesfully to the system!")

    return render(request, 'common/location.html',{"title":title,"list":list,"form":form})

@login_required
def allreports_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Reports"
    list = profile.objects.exclude(workStatus="Not Employeed")
    projs = projects.objects.all()

    return render(request, 'common/reports.html', {"title":title,"list":list,"projs":projs})


@login_required
def editprofile_View(request,staff_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    info = profile.objects.get(staffID=staff_id)
    user = User.objects.get(username=info.user.username)
    title = "Edit Profile of User: " + info.user.first_name + " " + info.user.last_name


    if request.method=="POST":
        form = UserUpdateForm(request.POST or None, instance=user)
        form2 = UserProfileForm(request.POST, request.FILES or None, instance=info)
        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            alert = alerts.objects.create(fromStaff=query, alertType='Edit Staff', alertDate=datetime.date.today(),
                                          info="Profile Edited")
            staffAlerts.objects.create(alertID=alert, staffID=info, status="Unseen")

            messages.success(request, info.user.first_name + " " + info.user.last_name + "'s account edited successfully!")
            return staffprofile_View(request,staff_id)
    else:
        form = UserUpdateForm(instance=user)
        form2 = UserProfileForm(instance=info)

    return render(request, 'staff/editprofile.html',{"title":title,"form":form,"form2":form2,"info":info})

@login_required
def editproject_View(request,project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    project = projects.objects.get(projectID=project_id)
    title = "Edit Project: " + project.projectName
    pms = profile.objects.filter(designation="Project Manager")
    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid() and request.POST:
        pm = request.POST.getlist("selectPM")
        update = form.save(commit=False)
        pmquery = profile.objects.get(staffID=pm[0])
        update.projectManager = pmquery
        update.save()
        messages.success(request, project.projectName + " edited successfully!")
        return projectprofile_View(request, project_id)

    return render(request,'project/editproject.html',{"title":title,"pms":pms,"project":project,"form":form})


@login_required
def alerttab_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Alerts"
    projectListUp = query.staffwithprojects_set.filter(Q(status="Working") & Q(projects_ID__status="Approved"))
    projectListOn = query.staffwithprojects_set.filter(Q(status="Working")&Q(projects_ID__status="On Going"))
    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by(
        '-alertID')
    return render(request,'common/alertTab.html',{"title":title,"alertList":alertList,"projectListOn":projectListOn,"projectListUp":projectListUp})

@login_required
def refresh_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')



    alertList = alerts.objects.filter(Q(staffalerts__staffID=query.staffID) & Q(staffalerts__status='Unseen')).order_by(
        '-alertID')
    alertids = {}

    for i,alert in enumerate(alertList):
            if i > 0:
                alertids.update({(alertList[i-1].alertID): alert})
            else:
                alertids.update({'abc': alert})
    return render(request,'common/refresh.html',{"alertList":alertList,"alertids":alertids})

@login_required
def alert_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Alerts"


    alertList = alerts.objects.filter(staff=query.staffID).order_by('-alertID')
    staff_id = str(query.staffID)
    alertids={}
    for alert in alertList:
        alertids.update({(alert.alertID-1):alert})
    if request.POST:
        if "rejectProj" in request.POST:
            id = request.POST.getlist("rejectProj")
            project = projects.objects.filter(projectID=id[0])
            info = projects.objects.get(projectID=id[0])
            project.update(status="Declined")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info) & Q(fromStaff=info.projectManager.staffID) & Q(alertType='Project'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Project Status Changed")
        elif "acceptProj" in request.POST:
            id = request.POST.getlist("acceptProj")
            project = projects.objects.filter(projectID=id[0])
            info = projects.objects.get(projectID=id[0])
            project.update(status="Approved")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info) & Q(fromStaff=info.projectManager.staffID) & Q(alertType='Project'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            msg = messageBoard.objects.create(projectID=info)
            boardComments.objects.create(board=msg, staff=query, comment="Welcome to the Message Board!",
                                         time=datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))
            messages.success(request, "Project Status Changed")
        elif "seen" in request.POST:
            alertID = request.POST.getlist('seen')
            alertObj = staffAlerts.objects.filter(Q(alertID=alertID[0]) & Q(staffID=query.staffID))
            alertObj.update(status="Seen")
        elif "rejectLeave" in request.POST:
            id = request.POST.getlist("rejectLeave")
            holiday = holidays.objects.filter(holidayID=id[0])
            info = holidays.objects.get(holidayID=id[0])
            holiday.update(status="Declined")
            print datetime.date.today()
            print info.startDate
            alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                          holiday=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.staffID, status="Unseen")
            alertobj = alerts.objects.get(Q(holiday=info) & Q(fromStaff=info.staffID.staffID) & Q(alertType='Leave'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Leave Status Changed")
        elif "acceptLeave" in request.POST:
            id = request.POST.getlist("acceptLeave")
            holiday = holidays.objects.filter(holidayID=id[0])
            info = holidays.objects.get(holidayID=id[0])
            time = datetime.date.today()
            staff = profile.objects.get(staffID=info.staffID_id)
            holiday.update(status="Approved")
            if info.startDate == time:
                staff.workStatus = "On Leave"
                staff.save()
            alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                          holiday=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.staffID, status="Unseen")
            alertobj = alerts.objects.get(Q(holiday=info) & Q(fromStaff=info.staffID.staffID)&Q(alertType='Leave'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Leave Status Changed")

    return render(request,'common/alerts.html',{"title":title,"alertList":alertList,"staff_id":staff_id})

@login_required
def requests_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Requests"


    alertList = alerts.objects.filter(Q(staff=query.staffID)&Q(alertType="Project")&Q(project__status="Pending Approval")|Q(alertType="Leave")&Q(holiday__status=
                                                                                                                                                 "Pending Approval")).order_by('-alertID')
    staff_id = str(query.staffID)

    if request.POST:
        if "rejectProj" in request.POST:
            id = request.POST.getlist("rejectProj")
            project = projects.objects.filter(projectID=id[0])
            info = projects.objects.get(projectID=id[0])
            project.update(status="Declined")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info) & Q(fromStaff=info.projectManager.staffID)&Q(alertType='Project'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Project Status Changed")
            return projectlist_View(request)
        elif "acceptProj" in request.POST:
            id = request.POST.getlist("acceptProj")
            project = projects.objects.filter(projectID=id[0])
            info = projects.objects.get(projectID=id[0])
            project.update(status="Approved")
            alert = alerts.objects.create(fromStaff=query, alertType='Project', alertDate=datetime.date.today(),
                                          project=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.projectManager, status="Unseen")
            alertobj = alerts.objects.get(Q(project=info) & Q(fromStaff=info.projectManager.staffID)&Q(alertType='Project'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            msg = messageBoard.objects.create(projectID=project)
            boardComments.objects.create(board=msg, staff=query, comment="Welcome to the Message Board!",
                                         time=datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))
            messages.success(request, "Project Status Changed")
            return projectlist_View(request)
        elif "rejectLeave" in request.POST:
            id = request.POST.getlist("rejectLeave")
            holiday = holidays.objects.filter(holidayID=id[0])
            info = holidays.objects.get(holidayID=id[0])
            holiday.update(status="Declined")
            alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                          holiday=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.staffID, status="Unseen")
            alertobj = alerts.objects.get(Q(holiday=info) & Q(fromStaff=info.staffID.staffID) & Q(alertType='Leave'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Leave Status Changed")
            return projectlist_View(request)
        elif "acceptLeave" in request.POST:
            id = request.POST.getlist("acceptLeave")
            holiday = holidays.objects.filter(holidayID=id[0])
            info = holidays.objects.get(holidayID=id[0])
            holiday.update(status="Approved")
            alert = alerts.objects.create(fromStaff=query, alertType='Leave', alertDate=datetime.date.today(),
                                          holiday=info)
            staffAlerts.objects.create(alertID=alert, staffID=info.staffID, status="Unseen")
            alertobj = alerts.objects.get(Q(holiday=info) & Q(fromStaff=info.staffID.staffID)&Q(alertType='Leave'))
            staffalert = staffAlerts.objects.filter(alertID=alertobj.alertID)
            staffalert.update(status="Seen")
            messages.success(request, "Leave Status Changed")
            return projectlist_View(request)

    return render(request,'common/requests.html',{"title":title,"alertList":alertList,"staff_id":staff_id})





@login_required
def report_View(request,project_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    # Create the HttpResponse object with the appropriate PDF headers.
    query = projects.objects.get(projectID=project_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Report.pdf"'


    # Create the PDF ob ject, using the response object as its "file."
    p = canvas.Canvas(response)
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/leidos_logo_2013.jpg')
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
    skillLevel = []
    staffList = query.staffwithprojects_set.filter(status="Working")
    for staff in staffList:

        skillLevel.append(staff.profile_ID.skillLevel)
    data = [skillLevel
            ]
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
    d.drawOn(p,10,500)

    d = Drawing()
    pie = Pie()
    pie.x = 200
    pie.y = 65
    pm = staffList.filter(profile_ID__designation="Project Manager").count()
    emp = staffList.filter(profile_ID__designation="Employee").count()
    cont = staffList.filter(profile_ID__designation="Contractor").count()

    total = staffList.count()

    pm = float(pm)/float(total) * 100
    emp = float(emp)/float(total) * 100
    cont = float(cont)/float(total) * 100

    pie.data = [pm, emp, cont]
    pie.labels = ["Project Manager " + str(round(pm, 2)) + "%", "Employee " + str(round(emp, 2)) + "%",
                  "Contractor: " + str(round(cont, 2)) + "%", ]
    pie.slices.strokeWidth = 0.5
    p.drawString(10, 530, "This graph shows different percantage of employee types working on this project")
    d.add(pie)
    d.drawOn(p, 10, 300)

    p.showPage()
    p.drawImage(fn, 0, 782, width=600, height=60)



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

@login_required
def matchmakingSelect_View(request):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Matchmaking"
    allProjects = projects.objects.all()

    return render(request, 'project/matchmaking.html', {"title": title,"allProjects":allProjects})


@login_required
def matchmaking_View(request,project_id):

    username = request.user
    query = profile.objects.get(user = username) #get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')

    title = "Matchmaking"
    allProjects = projects.objects.all()
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
    dict = {}
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
        alert = alerts.objects.create(fromStaff=query, alertType='Edit Project', alertDate=datetime.date.today(),
                                      project=project, info="Added Staff to Project")
        staffAlerts.objects.create(alertID=alert, staffID=project.projectManager, status="Unseen")
        return matchmakingSelect_View(request)

    return render(request,'project/matchmaking.html',{"title":title,"allProjects":allProjects,"full":full,"fsome":fsome,"partial":partial,"some":some,"project":project,"holidayID":holidayID,"dict":dict})

@login_required
def staffreport_View(request,staff_id):

    username = request.user
    query = profile.objects.get(user=username)  # get username

    if query.designation != "Admin":  # check if admin
        return render(request,'errorpermission.html')
    # Create the HttpResponse object with the appropriate PDF headers.
    query = profile.objects.get(staffID=staff_id)
    pdf = HttpResponse(content_type='application/pdf')
    pdf['Content-Disposition'] = 'attachment; filename="Report.pdf"'


    # Create the PDF ob ject, using the response object as its "file."
    p = canvas.Canvas(pdf)
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/leidos_logo_2013.jpg')
    p.drawImage(fn,0,782,width=600,height=60)


    p.drawString(210, 750, "Staff Report")
    # p.showPage()



    p.drawString(20, 710, "Staff ID: "+str(query.staffID))
    p.drawString(20, 690, "First Name: " + query.user.first_name)
    p.drawString(20, 670, "Last Type: " + query.user.last_name)
    p.drawString(20, 650, "Email: " + query.user.email)
    p.drawString(20, 600, "Nationality: " + query.nationality)
    p.drawString(20,580,"Preferred Country: "+query.preferredLocation.country+"    Preferred City: "+query.preferredLocation.city )
    p.drawString(200, 540, "Designation: "+query.designation)
    p.drawString(20,520,"Skill Level: "+str(query.skillLevel))
    p.drawString(20,500,"Date of Birth: "+str(query.dateOfBirth))
    p.drawString(20,480,"Skills: ")
    x = 460
    i = 1

    skillids = query.staffwithskills_set.values_list('skillID', flat=True)
    skillNames = []
    skillids = list(set(skillids))
    for id in skillids:
        skillNames.append(skills.objects.get(skillID=id))

    for skill in skillNames:
        p.drawString(140,x,str(i)+") "+skill.skillName)
        x = x - 20
        i = i + 1
    p.showPage()
    p.drawImage(fn, 0, 782, width=600, height=60)

    p.drawString(140, 750, "Projects")

    x = 710
    for project in query.projects_set.all():
        p.drawString(20,x,"Project ID: "+str(project.projectID)+"     Name: "+project.projectName)
        x = x - 20


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return pdf