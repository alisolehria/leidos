from django.db import models
from django.contrib.auth.models import User
from adminUser.models import location
import datetime


class profile(models.Model):
#this is profile table in db linked to users table
    class Meta:
        db_table = 'profile'

    picture = models.ImageField(upload_to='profilepic/',blank=True,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staffID = models.AutoField(primary_key=True)
    #profilePicture = models.ImageField(upload_to='\images')
    dateOfBirth = models.DateField()
    nationality = models.CharField(max_length=200)
    contact = models.CharField(max_length=12)
    preferredLocation = models.ForeignKey('adminUser.location')
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = models.CharField(max_length=6, choices=GENDER)
    DESIGNATIONS = (
        ('Admin','Admin'),
        ('Project Manager','Project Manager'),
        ('Employee','Employee'),
        ('Contractor','Contractor')
    )
    designation = models.CharField(max_length=15, choices=DESIGNATIONS)
    WORKSTATUS = (
        ('Working', 'Working'),
        ('On Leave ', 'On Leave'),
        ('Not Employeed', 'Not Employeed'),
    )
    workStatus = models.CharField(max_length=15, choices=WORKSTATUS)
    skillLevel = models.IntegerField()
    salary = models.IntegerField()

    def __unicode__(self):
        return str(self.staffID)




class previousWorkplaces(models.Model):

    class Meta:
        db_table = "previousWorkplaces"


    companyName = models.CharField(max_length=200)
    staffID = models.ForeignKey('profile')
    companyRating = models.IntegerField()

class projects(models.Model):
    class Meta:
        db_table = 'projects'

    projectID = models.AutoField(primary_key=True)
    staffID = models.ManyToManyField(profile,through="staffWithProjects")
    projectName = models.CharField(max_length=200)
    projectManager = models.ForeignKey('profile',related_name='+')
    TYPE = (
        ('Consultancy', 'Consultancy'),
        ('Development', 'Development'),
        ('Delivery', 'Delivery'),
        ('IT','IT')
    )
    type = models.CharField(max_length=30, choices=TYPE)
    location = models.ForeignKey('adminUser.location')
    startDate = models.DateField()
    endDate = models.DateField()
    description = models.TextField()
    budget = models.IntegerField()
    numberOfStaff = models.IntegerField()
    STATUS = (
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('On Going', 'On Going'),
        ('Completed', 'Completed'),
        ('Declined', 'Declined'),
        ('Discontinued', 'Discontinued'),
    )
    status = models.CharField(max_length=30, choices=STATUS)

    def __str__(self):
        return str(self.projectName)

class staffWithProjects(models.Model):

    class Meta:
        db_table = "staffWithProjects"

    projects_ID = models.ForeignKey(projects)
    profile_ID = models.ForeignKey(profile)
    STATUS = (
        ('Working', 'Working'),
        ('Not Working', 'Not Working'),
    )
    status = models.CharField(max_length=30, choices=STATUS,blank=True,null=True)
    startDate = models.DateField(blank=True,null=True)
    endDate = models.DateField(blank=True,null=True)




class skills(models.Model):

    class Meta:
        db_table = "skills"

    projectID = models.ManyToManyField(projects,through='projectsWithSkills')
    staffID = models.ManyToManyField(profile,through='staffWithSkills')
    skillID = models.AutoField(primary_key=True)
    skillName = models.CharField(max_length=200)
    PRIORITY = (
        ('High', 'High'),
        ('Mid', 'Mid'),
        ('Low', 'Low'),
    )
    priority = models.CharField(max_length=30, choices=PRIORITY)

    def __str__(self):
        return str(self.skillName)

class projectsWithSkills(models.Model):

    class Meta:
        db_table = "projectsWithSkills"

    projectID = models.ForeignKey(projects)
    skillID = models.ForeignKey(skills)
    hoursRequired = models.IntegerField()
    startDate = models.DateField()
    endDate = models.DateField()

    def __str__(self):
        return str(self.hoursRequired)

class staffWithSkills(models.Model):

    class Meta:
        db_table = "staffWithSkills"

    staffID = models.ForeignKey(profile)
    skillID = models.ForeignKey(skills)
    hoursAvailable = models.IntegerField()
    hoursLeft = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()


    def __str__(self):
        return str(self.hoursAvailable)


class holidays(models.Model):

    class Meta:
        db_table = "holidays"

    holidayID = models.AutoField(primary_key=True)
    staffID = models.ForeignKey(profile)
    startDate = models.DateField()
    endDate = models.DateField()
    STATUS = (
        ('Approved', 'Approved'),
        ('Pending Approval','Pending Approval'),
        ('Declined', 'Declined'),
    )
    TYPE = (
        ('Sick', 'Sick'),
        ('Emergency', 'Emergency'),
        ('Vacation', 'Vacation')
    )
    type = models.CharField(max_length=30,choices=TYPE)
    status = models.CharField(max_length=30, choices=STATUS)

    def __str__(self):
        return str(self.holidayID)

class alerts(models.Model):

    class Meta:
        db_table = "alerts"

    alertID = models.AutoField(primary_key=True)
    fromStaff = models.ForeignKey(profile,related_name='+')
    TYPE = (
        ('Project', 'Project'),
        ('Leave', 'Leave'),
        ('Staff', 'Staff'),
        ('Edit Project','Edit Project'),
        ('Edit Staff','Edit Staff'),
        ('Project Request','Project Request')
    )
    alertType = models.CharField(max_length=30, choices=TYPE)
    alertDate = models.DateField()
    staff = models.ManyToManyField(profile, blank=True,through='staffAlerts')
    project = models.ForeignKey('projects',blank=True,null=True)
    holiday = models.ForeignKey('holidays',blank=True,null=True)
    info = models.CharField(max_length=500,blank=True,null=True)


    def __str__(self):
        return str(self.alertID)


class staffAlerts(models.Model):
    class Meta:
        db_table = "staffAlerts"

    alertID = models.ForeignKey(alerts)
    staffID = models.ForeignKey(profile)
    STATUS = (
        ('Seen', 'Seen'),
        ('Unseen', 'Unseen'),
    )
    seenDate = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS,default='Unseen')

class staffProjectSkill(models.Model):
    class Meta:
        db_table = "staffProjectSkill"

    projectID = models.ForeignKey(projects)
    staffID = models.ForeignKey(profile)
    skillID = models.ForeignKey(skills)
    hours = models.IntegerField()
    month = models.IntegerField()

class messageBoard(models.Model):
    class Meta:
        db_table = "messageBoard"

    boardID =  models.AutoField(primary_key=True)
    projectID = models.ForeignKey(projects)
    comments = models.ManyToManyField(profile,through="boardComments")


class boardComments(models.Model):
    class Meta:
        db_table = "boardComments"

    board = models.ForeignKey(messageBoard)
    staff = models.ForeignKey(profile)
    comment = models.TextField()
    time =  models.CharField(max_length=100)
