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