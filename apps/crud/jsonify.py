from apps.crud import models as DB
from apps.app import db



def json_SeniorSetting(user: DB.Elder):
    fields = [
        "id", "name", "addScheduleFromProtectorAlarm", "addMessageFromProtectorAlarm",
        "isFallDetect", "isGetWellnessQuestion", "makeWellnessReport", "detectFallEvent",
        "alarmFallSuspicious", "realTimeFallReport", "isCallAlarm", "choiceVoice", "memo"
    ]

    if isinstance(user, DB.Elder):
        SeniorSetting = {field: getattr(user, field) for field in fields}
    else:
        SeniorSetting = {field: None for field in fields}

    return SeniorSetting

def json_ProtectorSetting(user: DB.Guardian):
    fields = [
        "id", "name", "completeScheduleAlarm", "fallDetectAlarm", "getReportAlarm"
    ]

    if isinstance(user, DB.Guardian):
        ProtectorSetting = {field: getattr(user, field) for field in fields}
    else:
        ProtectorSetting = {field: None for field in fields}

    return ProtectorSetting

def json_ProtectorInfo(user: DB.Elder):
    ProtectorInfo = {
        "count": 0,
        "lists": []
    }

    #? 보호자는 바로 반환
    if isinstance(user, DB.Guardian):
      return ProtectorInfo

    relationships = DB.CareRelationship.query.filter(
        DB.CareRelationship.elder_id == user.id
    ).all()

    for relationship in relationships:
        guardian = DB.Guardian.query.filter(
            DB.Guardian.id == relationship.guardian_id
        ).first()

        pInfo = {
            "id": guardian.id,
            "name": guardian.name,
            "callNumber": guardian.phone,
            "permLocation": relationship.perm_location,
            "permSchedule": relationship.perm_schedule,
            "permMessage": relationship.perm_message,
            "permReport": relationship.perm_report,
            "permFallDetect": relationship.perm_fall_detect
        }

        ProtectorInfo['count'] += 1
        ProtectorInfo['lists'].append(pInfo)

    return ProtectorInfo

def json_SeniorInfo(user: DB.Guardian):
    SeniorInfo = {
        "count": 0,
        "lists": []
    }

        #? 고령자는 바로 반환
    if isinstance(user, DB.Elder):
        return SeniorInfo

    relationships = DB.CareRelationship.query.filter(
        DB.CareRelationship.guardian_id == user.id
    ).all()

    for relationship in relationships:
        elder = DB.Elder.query.filter(
            DB.Elder.id == relationship.elder_id
        ).first()

        sInfo = {
            "id": elder.id,
            "name": elder.name,
            "callNumber": elder.phone
        }

        SeniorInfo['count'] += 1
        SeniorInfo['lists'].append(sInfo)

    return SeniorInfo


def json_ScheduleItem(user: DB.Elder):
    ScheduleItem = {
        "count": 0,
        "lists": []
    }

    if isinstance(user, DB.Elder):
        elder_id = user.id
    else:
        elder_id = user.main_elder_id

    schedules = DB.Schedule.query.filter(
        DB.Schedule.elder_id == elder_id
    ).order_by(
        DB.Schedule.start_year,
        DB.Schedule.start_month,
        DB.Schedule.start_day,
        DB.Schedule.start_hour,
        DB.Schedule.start_minute
    ).all()

    ScheduleItem['count'] = len(schedules)

    for schedule in schedules:
        sItem = {
            "id": schedule.id,
            "title": schedule.title,
            "startYear": schedule.start_year,
            "startMonth": schedule.start_month,
            "startDay": schedule.start_day,
            "startHour": schedule.start_hour,
            "startMinute": schedule.start_minute,
            "endYear": schedule.end_year,
            "endMonth": schedule.end_month,
            "endDay": schedule.end_day,
            "endHour": schedule.end_hour,
            "endMinute": schedule.end_minute,
            "memo": schedule.memo,
            "doAlarm": schedule.do_alarm,
            "confirmAlarmMinute": schedule.confirm_alarm_minute,
            "isComplete": schedule.is_complete
        }
        ScheduleItem['lists'].append(sItem)

    return ScheduleItem


def json_MedicineItem(user: DB.Elder):
    MedicineItem = {
        "count": 0,
        "lists": []
    }

    if isinstance(user, DB.Guardian):
        elder_id = user.main_elder_id
    else:
        elder_id = user.id

    medicines = DB.Medicine.query.filter(
        DB.Medicine.elder_id == elder_id
    ).order_by(
        DB.Medicine.start_year,
        DB.Medicine.start_month,
        DB.Medicine.start_day
    ).all()

    MedicineItem['count'] = len(medicines)

    for medicine in medicines:
        mItem = {
            "id": medicine.id,
            "title": medicine.title,  # Assuming there's a title field in the medicine model
            "startYear": medicine.start_year,
            "startMonth": medicine.start_month,
            "startDay": medicine.start_day,
            "endYear": medicine.end_year,
            "endMonth": medicine.end_month,
            "endDay": medicine.end_day,
            "medicinePeriod": medicine.medicine_period,
            "memo": medicine.memo,
            "doAlarm": medicine.do_alarm,
            "confirmAlarmMinute": medicine.confirm_alarm_minute,
        }

        MedicineItem['lists'].append(mItem)

    return MedicineItem


def json_MessageItem(user: DB.Elder):
    MessageItem = {
        "count": 0,
        "lists": []
    }

    #? 고령자는 고령자가 받은 메시지만
    if isinstance(user, DB.Elder):
        messages = DB.Message.query.filter(
            DB.Message.elder_id == user.id
        ).order_by(
            DB.Message.year,
            DB.Message.month,
            DB.Message.day,
            DB.Message.hour,
            DB.Message.minute
        ).all()
    #? 보호자는 보호자가 main 고령자에게 보낸 메시지만
    else:
        messages = DB.Message.query.filter(
            DB.Message.elder_id == user.main_elder_id,
            DB.Message.guardian_id == user.id
        ).order_by(
            DB.Message.year,
            DB.Message.month,
            DB.Message.day,
            DB.Message.hour,
            DB.Message.minute
        ).all()

    MessageItem['count'] = len(messages)

    for msg in messages:
        mItem = {
            "id": msg.id,
            "title": msg.title,
            "year": msg.year,
            "month": msg.month,
            "day": msg.day,
            "hour": msg.hour,
            "minute": msg.minute,
            "content": msg.content,
            "doAlarm": msg.do_alarm,
            "alarmType": msg.alarm_type
        }

        MessageItem['lists'].append(mItem)

    return MessageItem


def json_MedicineAlarmItem(user: DB.Elder):
    MedicineAlarmItem = {
        "count": 0,
        "lists": []
    }

    if isinstance(user, DB.Elder):
        elder_id = user.id
    else:
        elder_id = user.main_elder_id




    medicineAlarms = DB.MedicineAlarm.query.filter(
        DB.MedicineAlarm.elder_id == elder_id
    ).order_by(
        DB.MedicineAlarm.year,
        DB.MedicineAlarm.month,
        DB.MedicineAlarm.day,
        DB.MedicineAlarm.hour,
        DB.MedicineAlarm.minute
    ).all()

    MedicineAlarmItem['count'] = len(medicineAlarms)

    for alarm in medicineAlarms:
        medicine = DB.Medicine.query.filter(
            DB.Medicine.id == alarm.medicine_id
        ).first()
        mItem = {
            "id": alarm.id,
            "title": medicine.title,
            "year": alarm.year,
            "month": alarm.month,
            "day": alarm.day,
            "hour": alarm.hour,
            "minute": alarm.minute,
            "memo": alarm.memo,
            "doAlarm": alarm.do_alarm,
            "confirmAlarmMinute": alarm.confirm_alarm_minute,
            "isComplete": alarm.is_complete
        }


        MedicineAlarmItem['lists'].append(mItem)

    return MedicineAlarmItem