from django.contrib import admin
from .models import Group, GroupList, Student, Person, Teacher
# Register your models here.

admin.site.register(Group)
admin.site.register(GroupList)
admin.site.register(Student)
admin.site.register(Person)
admin.site.register(Teacher)