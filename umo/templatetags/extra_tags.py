from django import template
from django.contrib.auth.models import Group
from ..models import Semester

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return Group.objects.get(name=group_name) in user.groups.all()


@register.filter
def get_maxpoint(max_points, checkpoint):
    return str(max_points[checkpoint.id]) if checkpoint.id in max_points.keys() else ''


@register.filter
def get_list(group_dict, edu_program):
    if edu_program.id in group_dict.keys():
        return ', '.join(group_dict[edu_program.id]) if edu_program else ''
    else:
        return ''


@register.simple_tag
def get_brs_point(student_points, student_id, checkpoint_id):
    return str(student_points[student_id][checkpoint_id])


@register.filter(name='get_exam_marks_for_semester')
def get_exam_marks_for_semester(student, semester):
    #print(semester)
    #print(student.exammarks_set.all())
    return student.exammarks_set.filter(exam__course__discipline_detail__semester=semester)


@register.filter(name='get_semesters_for_year')
def get_semesters_for_year(year):
    return Semester.objects.filter(year=year)


@register.filter(name='has_scores_for_year')
def has_scores_for_year(year, student):
    semesters = get_semesters_for_year(year)
    for semester in semesters:
        return get_exam_marks_for_semester(student, semester)
