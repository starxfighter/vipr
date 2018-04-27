from __future__ import unicode_literals
from django.db import models
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # first name checks
        if postData['fname'] == "":
            errors['fname'] = "A first name is required"
        elif  len(postData['fname']) < 2:
            errors['fname'] = "A first name has to be more than two characters"
        elif postData['fname'].isalpha() == False:
            errors['fname'] = "A first name can not contain any numbers or special characters"
        # las name checks
        if postData['lname'] == "":
            errors['lname'] = "A last name is required"
        elif  len(postData['lname']) < 2:
            errors['lname'] = "A last name has to be more than two characters"
        elif postData['lname'].isalpha() == False:
            errors['lname'] = "A last name can not contain any numbers or special characters"
        # email checks
        if postData['email'] == "":
            errors['email'] = "An email is required."
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Your email is not the correct format."
        # branch of service checks
        if postData['svc_branch'] == "":
            errors['svc_branch'] = "A service branch must be selected"
        # military ID checks
        if postData['milid'] == "":
            errors['milid'] = "A military id number is required"
        elif  len(postData['milid']) < 8:
            errors['milid'] = "A military id has to contain 8 numerics"
        # password checks
        if len(postData['password']) < 8:
            errors['password'] = "Your password must be at least 8 characters long"
        elif postData['password'] != postData['pass_conf']:
            errors['password'] = "Your password does not match your confirm password"
        # pay service level checks
        if postData['pay_svc_lvl'] == "":
            errors['pay_svc_lvl'] = "A pay service level must be selected"
        return errors

    def create_user(self, postData):
        pwd = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
        new_user = User.objects.create(first_name = postData['fname'], 
            last_name = postData['lname'], 
            email = postData['email'], 
            service_branch = postData['svc_branch'],
            military_id = postData['milid'],
            password = pwd.decode('utf-8'),
            sys_access_level = 1,
            pay_svc_level = postData['pay_svc_lvl'])
        return new_user

class RequestManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # Request checks
        print(postData)
        if postData['reqdesc'] == "":
            errors['reqdesc'] = "A request can not be blank. Please re-enter."
        elif  len(postData['reqdesc']) < 10:
            errors['reqdesc'] = "A request is typically more than 10 characters long. Please be specific in your request"
        return errors

    def create_request(self, postData, user):
        new_request = Request.objects.create(req_desc = postData['reqdesc'],
            req_res = " ",
            requester = user) 
        return new_request


class User(models.Model):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    service_branch = models.CharField(max_length = 20)
    military_id = models.IntegerField()
    password = models.CharField(max_length = 255)
    sys_access_level = models.SmallIntegerField()
    pay_svc_level = models.CharField(max_length = 20)
    charge_id = charge_id   = models.CharField(max_length=234)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Request(models.Model):
    req_desc = models.CharField(max_length = 255)
    req_res = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    requester = models.ForeignKey(User, related_name = 'request_for', on_delete = models.CASCADE)
    objects = RequestManager()


class Document(models.Model):
    document = models.FileField(upload_to='document/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    documenter = models.ManyToManyField(Request, related_name = 'document_for')