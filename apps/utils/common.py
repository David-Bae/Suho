# 고령자-보호자 계정에서 약 추가
from apps.crud import models as DB
from apps.app import db
from datetime import date, datetime, timedelta

def add_medicine(elder_id, title, start_year, start_month, start_day,
                 end_year, end_month, end_day, medicine_period, memo,
                 do_alarm, confirm_alarm_minute):

    new_medicine = DB.Medicine(title=title, elder_id=elder_id, start_year=start_year,
                               start_month=start_month, start_day=start_day, end_year=end_year,
                               end_month=end_month, end_day=end_day, medicine_period=medicine_period,
                               memo=memo, do_alarm=do_alarm, confirm_alarm_minute=confirm_alarm_minute)

    db.session.add(new_medicine)
    db.session.commit()

    period_times = {
        0: [(8, 0)],  # 일어나서 1회 (8:00 AM)
        1: [(22, 0)],  # 자기전 1회 (10:00 PM)
        2: [(8, 0), (20, 0)],  # 아침저녁 (8:00 AM, 8:00 PM)
        3: [(8, 0), (12, 0), (18, 0)],  # 아침점심저녁 (8:00 AM, 12:00 PM, 6:00 PM)
        4: [(8, 0)]  # 기타 (default to 8:00 AM)
    }

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    current_date = start_date

    alarm_times = period_times[medicine_period]

    while current_date <= end_date:
        for time in alarm_times:
            hour, minute = time
            medicine_time = datetime(current_date.year, current_date.month, current_date.day, hour, minute)
            alarm_time = medicine_time - timedelta(minutes=do_alarm)
            new_alarm = DB.MedicineAlarm(
                medicine_id=new_medicine.id,
                elder_id=elder_id,
                year=alarm_time.year,
                month=alarm_time.month,
                day=alarm_time.day,
                hour=alarm_time.hour,
                minute=alarm_time.minute,
                do_alarm=True,
                confirm_alarm_minute=confirm_alarm_minute
            )
            db.session.add(new_alarm)
        current_date += timedelta(days=1)

    db.session.commit()


def add_schedule(elder_id, title, start_year, start_month, start_day, start_hour, start_minute,
                 end_year, end_month, end_day, end_hour, end_minute, memo, do_alarm, confirm_alarm_minute):
    new_schedule = DB.Schedule(
        elder_id=elder_id, 
        title=title, 
        start_year=start_year, 
        start_month=start_month, 
        start_day=start_day, 
        start_hour=start_hour, 
        start_minute=start_minute,
        end_year=end_year, 
        end_month=end_month, 
        end_day=end_day, 
        end_hour=end_hour, 
        end_minute=end_minute, 
        memo=memo, 
        do_alarm=do_alarm,
        confirm_alarm_minute=confirm_alarm_minute
    )

    db.session.add(new_schedule)
    db.session.commit()