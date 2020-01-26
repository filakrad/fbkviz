from datetime import timedelta


def get_next_day(day):
    '''
    :param day: date of a day in date format
    :return: next day that is not weekend
    '''
    day_of_week = day.weekday()
    if day_of_week < 4:
        return day + timedelta(days=1)
    else:
        return day + timedelta(days=(7-day_of_week))


def get_next_monday(day):
    '''
    Gets date of next monday from a date
    :param day: some date
    :return: date of next monday
    '''
    weekday = day.weekday()
    monday = 7 - weekday
    next_day = day + timedelta(days=monday)
    return next_day
