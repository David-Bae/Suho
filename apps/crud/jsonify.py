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


