from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Login_Table(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    contact_details = models.CharField(max_length=100)
    skills = models.TextField()
    brief_description = models.TextField()
    profile_pic = models.ImageField()
    login = models.ForeignKey(Login_Table, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True, default=1)

    def __str__(self):
        return self.name

class Director(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    contact_details = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    brief_description = models.TextField()
    login = models.ForeignKey(Login_Table, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    id_file = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.name
class Talents(models.Model):
    talent = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Talent'
        verbose_name_plural = 'Talents'

    def __str__(self):
        return self.talent

class Place(models.Model):
    country = models.CharField(max_length=100, default='Unknown')
    state = models.CharField(max_length=100, default='Unknown')
    city = models.CharField(max_length=100, default='Unknown')
    pin_code = models.CharField(max_length=20, default='Unknown')

    class Meta:
        verbose_name = 'Place'
        verbose_name_plural = 'Places'

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country} - {self.pin_code}"
    
class Post(models.Model):
    role = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    talent_category = models.ForeignKey(Talents, on_delete=models.CASCADE, null=True, blank=True)
    media = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.description[:50]