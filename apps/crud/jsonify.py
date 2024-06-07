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