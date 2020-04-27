from django.db import transaction
from umo.models import EduOrg, Kafedra, EduProgram, Specialization, Discipline, \
    DisciplineDetails, Profile, Year, Semester, Teacher, Control, Position, BRSpoints
from umo.objgens import check_edu_org
import xml.etree.ElementTree as ET
import re


def exclude_disciplines_from_program(education_program, including_disciplines=[], except_discipline=[]):
    disciplines = Discipline.objects.filter(program=education_program)
    if len(including_disciplines) > 0:
        disciplines = disciplines.filter(id__in=including_disciplines)
    if len(except_discipline) > 0:
        disciplines = disciplines.exclude(id__in=except_discipline)
    for dis in disciplines:
        if not BRSpoints.objects.filter(course__discipline_detail__discipline__id=dis.id, points__gt=0).exists():
            dis.delete()


def get_qualification(name, program_code=''):
    name = name.lower()
    if name == '1':
        return 1
    elif name == '2':
        if program_code == '3':
            return 4
        elif program_code == '4':
            return 5
        return 2
    elif name == '3':
        if program_code == '3':
            return 6
        elif program_code == '4':
            return 7
        return 3
    elif name == '7':
        return 8
    elif name == '10':
        return 9
    return 0


@transaction.atomic
def parseRUP_fgos3plusplus(filename, kaf):
    #name_file_xml = os.path.join('upload', filename)
    ns = '{http://tempuri.org/dsMMISDB.xsd}'
    tree = ET.parse(filename)
    root = tree.getroot()
    #имя плана
    name = root.get('LastName')
    root = root[0][0]
    #Уровень образования
    oop = root.find(ns+'ООП')
    level = 2 if oop.get('УровеньОбразования') == '3' else 1
    #тэг Специальность получение названия спец
    #specs = oop.get('Название')
    spec_name = oop.get('Название')
    #тэг Специальность ном2 получения названия профиль
    profile_name = 'Общий'
    profile_oop = oop.find(ns + 'ООП')
    if profile_oop is not None:
        profile_name = profile_oop.get('Название',)
    qual_name = oop.get('Квалификация', '')
    program_code = root.find(ns + 'Планы').get('КодПрограммы','')

    code = oop.get('Шифр','')
    yearp = root.find(ns + 'Планы').get('ГодНачалаПодготовки')

    year, created = Year.objects.get_or_create(year=yearp)

    sp, created = Specialization.objects.get_or_create(code=code, defaults={
        'name': spec_name,
        'brief_name': '',
        'qual': get_qualification(qual_name, program_code),
        'level': level
    })
    profile, created = Profile.objects.get_or_create(name=profile_name, spec=sp)

    edu_prog, created = EduProgram.objects.get_or_create(specialization=sp, profile=profile, cathedra=kaf, year=year, name=name)

    disciplines = root.findall(ns + 'ПланыСтроки')
    controls = {"1": 1, "2": 2, "3": 3, "4": 5, "5": 4, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "49": 49}
    ids = []
    for d in disciplines:
        d_code = d.get('ДисциплинаКод', '')
        obj_code = d.get('Код', '')
        d_name = d.get('Дисциплина','')
        dis, created = Discipline.objects.update_or_create(code=d_code, program=edu_prog, defaults={'name': d_name})
        ids.append(dis.id)
        data = {}
        hours = root.findall(ns + 'ПланыНовыеЧасы[@КодОбъекта="' + obj_code + '"][@КодТипаЧасов="1"]')
        for item in hours:
            edu_year = int(item.get('Курс',0))
            semester = int(item.get('Семестр',0))
            semester = str(2*(edu_year - 1) + semester)
            if semester not in data.keys():
                data[semester] = {
                    'hours': {'101': 0, '102': 0, '103': 0, '104': 0, '105': 0, '106': 0, '107': 0, '108': 0, '109': 0, '110': 0,
                              '111': 0, '112': 0, '113': 0, '114': 0, '115': 0, '116': 0, '117': 0, '118': 0, '119': 0, '139': 0,
                              '140': 0, '141': 0, '142': 0},
                    'control': {},
                    'zed' : 0
                    }
            w_type = item.get('КодВидаРаботы', '0')
            if w_type in data[semester]['hours'].keys():
                data[semester]['hours'][w_type] = int(item.get('Количество', '0'))
            elif w_type in controls.keys():
                data[semester]['control'][controls[w_type]] = int(item.get('Количество','0'))
            elif w_type == '50':
                data[semester]['zed'] = int(item.get('Количество','0'))
        for key in data.keys():
            semester, created = Semester.objects.get_or_create(name=key)
            defaults = {'Credit': data[key]['zed'],
                        'Lecture': data[key]['hours']['101'],
                        'Practice': data[key]['hours']['103'],
                        'Lab': data[key]['hours']['102'],
                        'KSR': data[key]['hours']['106'],
                        'SRS': data[key]['hours']['107']}
            dd, created = DisciplineDetails.objects.update_or_create(discipline=dis,
                                                                     semester=semester,
                                                                     defaults=defaults)
            dd.control_set.all().delete()
            for control_type in data[key]['control'].keys():
                c, created = Control.objects.update_or_create(discipline_detail=dd, control_type=control_type,
                                                              defaults={'control_hours': data[key]['control'][control_type]})
    exclude_disciplines_from_program(edu_prog, except_discipline=ids)


def get_qualification_fgos3(name):
    name = name.lower()
    if 'специали' in name:
        return 1
    elif 'бакалавр' in name:
        if 'академ' in name:
            return 4
        elif 'приклад' in name:
            return 5
        return 2
    elif 'магистр' in name:
        return 3
    return 0


def get_education_level_fgos3(name):
    name = name.lower()
    if 'спо' in name:
        return 1
    elif 'впо' in name:
        return 2
    return 0


@transaction.atomic
def parseRUP_fgos3(filename, kaf):
    #name_file_xml = os.path.join('upload', filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    title = root[0][0]
    name = title.get('ПолноеИмяПлана')
    #Уровень образования
    level = root[0].get('УровеньОбразования')
    #тэг Специальность получение названия спец
    specs = title.find('Специальности')
    spec_name = ' '.join(specs[0].get('Название').split()[1:])
    #тэг Специальность ном2 получения названия профиль
    if len(specs) > 1:
        profile_name = ' '.join(specs[1].get('Название').split()[1:])
    else:
        profile_name = 'Общий'
    #qual = root[0][0][7][0] #тэг Квалификация получения квалиф
    qual_name = title.find('Квалификации')[0].get('Название')
    #code = root[0][0] #тэг План получения КодКафедры и ПоследнийШифр
    code = title.get('ПоследнийШифр')
    yearp = title.get('ГодНачалаПодготовки')

    year, created = Year.objects.get_or_create(year=yearp)

    sp, created = Specialization.objects.get_or_create(code=code, defaults={
        'name': spec_name,
        'brief_name': '',
        'qual': get_qualification_fgos3(qual_name),
        'level': get_education_level_fgos3(level)
    })
    profile, created = Profile.objects.get_or_create(name=profile_name, spec=sp)

    edu_prog, created = EduProgram.objects.get_or_create(specialization=sp, profile=profile, cathedra=kaf, year=year, name=name)
    ids = []
    for elem in root[0][1]:
        disname = elem.get('Дис')
        code_dis = elem.get('ИдетификаторДисциплины')
        new_code = elem.get('НовИдДисциплины', code_dis)
        dis_kaf = elem.get('Кафедра', None)
        if dis_kaf is None or len(dis_kaf) < 1:
            continue

        dis = Discipline.objects.filter(code=code_dis, program=edu_prog, name=disname).first()
        if dis is None:
            dis = Discipline.objects.filter(code=new_code, program=edu_prog, name=disname).first()
        if dis is None:
            dis = Discipline.objects.create(name=disname, code=new_code, program=edu_prog)
        else:
            dis.name = disname
            dis.code = new_code
            dis.save()
        ids.append(dis.id)
        for details in elem.findall('Сем'):
            #if details is ('Ном' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Пр' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Лаб' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Лаб' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Пр') or ('Ном' and 'СРС'):
            data = {'101': 0, '102': 0, '103': 0, '106': 0, '107': 0, '108': 0}
            total_h = 0
            for vz in details.findall('VZ'):
                if 'H' in vz.attrib.keys():
                    data[vz.get("ID")] = int(vz.get('H'))
                    total_h += int(vz.get('H'))
            if total_h < 1:
                continue

            #semester_nom = '1'
            semester_nom = details.get('Ном','1')
            zet = details.get('ЗЕТ','1')
            z = details.get('Зач', None)
            exam = details.get('Экз', None)
            zO = details.get('ЗачО', None)
            CW = details.get('КР', None)

            semester, created = Semester.objects.get_or_create(name=semester_nom)
            defaults={'Credit': int(zet),
                      'Lecture': data['101'],
                      'Practice': data['103'],
                      'Lab': data['102'],
                      'KSR': data['106'],
                      'SRS': data['107']}
            d, created = DisciplineDetails.objects.update_or_create(discipline=dis,
                                                                    semester=semester,
                                                                    defaults=defaults)
            d.control_set.all().delete()
            if z is not None:
                c, created = Control.objects.get_or_create(discipline_detail=d, control_type=2,
                                                           defaults={'control_hours': data['108']})
            if exam is not None:
                c, created = Control.objects.get_or_create(discipline_detail=d, control_type=1,
                                                           defaults={'control_hours': data['108']})
            if zO is not None:
                c, created = Control.objects.get_or_create(discipline_detail=d, control_type=3,
                                                           defaults={'control_hours': data['108']})
            if CW is not None:
                c, created = Control.objects.get_or_create(discipline_detail=d, control_type=4,
                                                           defaults={'control_hours': 0})
    exclude_disciplines_from_program(edu_prog, except_discipline=ids)


def parseRUP(filename, cathedra):
    if '.plx' in filename:
        parseRUP_fgos3plusplus(filename, cathedra)
    else:
        parseRUP_fgos3(filename, cathedra)