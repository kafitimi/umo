from umo.models import EduOrg, Kafedra, EduProg, Specialization, Discipline, \
    DisciplineDetails, Profile, Year, Semestr, Qual, Level, Teacher, Control, Position, Zvanie
import xml.etree.ElementTree as ET



def parseRUP(filename):
    #name_file_xml = os.path.join('upload', filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    #specialization = root[0][0][3][0] #тэг Специальность получение названия спец
    spec_name = ' '.join(root[0][0][3][0].get('Название').split()[1:])
    print(spec_name)

    #profil = root[0][0][3][1] #тэг Специальность ном2 получения названия профиль
    profil_name = ' '.join(root[0][0][3][1].get('Название').split()[1:])
    print(profil_name)

    #qual = root[0][0][7][0] #тэг Квалификация получения квалиф
    qual_name = ' '.join(root[0][0][7][0].get('Название').split()[1:])
    print(qual_name)

    #code = root[0][0] #тэг План получения КодКафедры и ПоследнийШифр
    name_institute = root[0][0].get('ИмяВуза2')
    name_university = root[0][0].get('ИмяВуза')
    code_kaf = root[0][0].get('КодКафедры')
    cipher = ''.join(str(i) for i in (root[0][0].get('ПоследнийШифр')).split('.'))
    yearp = root[0][0].get('ГодНачалаПодготовки')
    print(name_institute)
    print(name_university)
    print(code_kaf)
    print(cipher)
    print(yearp)

    name_inst = EduOrg.objects.filter(name=name_institute).first()
    if name_inst is None:
        name_inst = EduOrg()
        name_inst.name = name_institute
        name_inst.uni = EduOrg.objects.filter(name__icontains='свфу').first()
        name_inst.save()
    else:
        name_insti = EduOrg()
        name_insti.name =name_inst
        name_insti.uni = EduOrg.objects.filter(name__icontains='свфу').first()
        name_insti.save()

    kaf = Kafedra.objects.filter(number=code_kaf).first()
    if kaf is None:
        kaf = Kafedra()
        kaf.number = code_kaf
        kaf.name = Kafedra.objects.filter(name='Информационные технологии').first()
        kaf.institution = name_inst
        kaf.save()
    else:
        kafd = Kafedra()
        kafd.number = kaf
        kafd.name = Kafedra.objects.filter(name='Информационные технологии').first()
        kafd.institution = name_inst
        kafd.save()



    #e = EduProg()
    sp = Specialization.objects.filter(name=spec_name).first()
    if sp is None:
        sp = Specialization()
        sp.name = spec_name
        sp.briefname = ""
        sp.code = cipher

        qual = Qual.objects.filter(name=qual_name).first()
        if qual is None:
            qual = Qual()
            qual.name = qual_name
            qual.save()
        sp.qual = qual

        level = Level()
        level.name = ""
        level.save()
        sp.level = level
        sp.save()
    #e.specialization = sp

    edu_prog = EduProg.objects.filter(specialization__name=spec_name).first()
    if edu_prog is None:
        edu_prog = EduProg()
        edu_prog.specialization = sp
        edu_prog.save()


        profil = Profile.objects.filter(name=profil_name).first()
        if profil is None:
            profil = Profile()
            profil.name = profil_name
            profil.save()
        edu_prog.profile = profil

        year = Year.objects.filter(year=yearp).first()
        if year is None:
            year = Year()
            year.year = yearp
            year.save()
        edu_prog.year = year

        edu_prog.cathedra = kaf


    for elem in root[0][1]:
        disname = elem.get('Дис')
        #code_dis = ''.join(str(i) for i in (elem.get('ИдетификаторДисциплины')).split('.'))
        code_dis = elem.get('ИдетификаторДисциплины')
        #time_zet = elem.get('ЧасовВЗЕТ')
        print(disname)
        print(code_dis)
        #print(time_zet)

        dis = Discipline.objects.filter(Name=disname).first()
        if dis is None:
            dis = Discipline()
            dis.Name = disname
            dis.code = code_dis
            dis.program = edu_prog

            lect = Teacher()
            lect.FIO = ""
            position = Position()
            position.name = ""
            position.save()
            lect.Position = position
            zvanie = Zvanie()
            zvanie.name = ""
            zvanie.save()
            lect.Zvanie = zvanie
            lect.cathedra = kaf
            lect.save()

            dis.lecturer = lect
            control = Control()
            control.controltype = ""
            control.save()
            dis.control = control
            dis.save()

        for details in elem.findall('Сем'):
            #if details is ('Ном' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Пр' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Лаб' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Лек' and 'Лаб' and 'Пр' and 'КСР' and 'СРС' and 'ЗЕТ') or ('Ном' and 'Пр') or ('Ном' and 'СРС'):
            data = {'101':0,'102':0,'103':0,'106':0,'107':0,'108':0}
            total_h = 0
            for vz in details.findall('VZ'):
                if hasattr(vz,'H'):
                    data[vz.get("ID")] = int(vz.get('H'))
                    total_h += int(vz.get('H'))
            if total_h < 1:
                continue
            semestr_nom = '1'
            if hasattr(details, 'Ном'):
                semestr_nom = details.get('Ном')
            zet = 1
            if hasattr(details, 'ЗЕТ'):
                zet = int(details.get('ЗЕТ'))

            d = DisciplineDetails()
            smstr = Semestr.objects.filter(name=semestr_nom).first()
            if smstr is None:
                smstr = Semestr()
                smstr.name = semestr_nom
                smstr.save()
            d.semestr = smstr
            d.subject = dis
            d.Credit = zet
            d.Lecture = data['101']
            d.Lab = data ['102']
            d.Practice = data['103']
            d.KSR = data['106']
            d.SRS = data['107']
            d.control_hours = ['108']
            d.save()