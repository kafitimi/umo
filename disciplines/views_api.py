import json

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse

from umo.models import BRSpoints, CheckPoint


@login_required
@permission_required('umo.change_brspoints', login_url='login')
def brs_scores(request):
    result = {"result":False}
    status = 200
    serialized_data = request.body.decode("utf-8")
    serialized_data = json.loads(serialized_data)
    scores = BRSpoints.objects.select_related('student', 'course').filter(course__id=serialized_data['course_id'], student__id=serialized_data['student_id'])
    if not scores:
        status = 404
    elif request.user.id != scores[0].course.lecturer.user.id:
        status=403
    else:
        result = {
            "student_id": str(scores[0].student.id),
            "course_id": str(scores[0].course.id),
            "fullname": str(scores[0].student.FIO)
        }
        with transaction.atomic():
            for score in scores:
                score.points = serialized_data['checkpoint_' + str(score.checkpoint.id)]
                result['checkpoint_' + str(score.checkpoint.id)] = serialized_data['checkpoint_' + str(score.checkpoint.id)]
                score.save()
    return HttpResponse(
        json.dumps(result),
        content_type='application/json',
        status=status
    )