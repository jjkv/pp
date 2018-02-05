# interface for parsing time strings into minutes from start of week
# also used for error checking interval form inputs

# this is not elegant or fast, but i think it works

# public list needed for various functions, i wish this language had const
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

MINS_PER_HOUR = 60
MINS_PER_DAY = 1440
MINS_PER_WEEK = 10080
SUNDAY_MINUTES = 8640

HOURS_PER_DAY = 24
NOON = 12

from flask import flash

assert(MINS_PER_HOUR * HOURS_PER_DAY == MINS_PER_DAY)

def min_str(m):
    sm = str(m)
    if len(sm) != 2:
        raise Exception('len of minute submission must be 2 (e.g. 04, 13, 59, etc)')
    if not sm[0].isdigit():
        raise Exception('minute submission must be a number')
    elif not sm[1].isdigit():
        raise Exception('minute submission must be a number')
    if int(sm)> 59:
        raise Exception('minutes cannot be greater than 59')
    return sm

def hour_str(h):
    return str(h)

def form_data_to_timestr(h, m):
    return hour_str(h)+':'+min_str(m)

# possibly needs more error checking
# gets the 45 from '1:45am'
def parse_mins(s):
    after = s.split(':')[1]
    after = after.replace(' ','')
    if len(after) != 4 and len(after) != 2:
        raise Exception('illformed time: bad minutes')
    mins = int((s.partition(':')[2])[:2])
    if mins >= MINS_PER_HOUR:
        raise Exception('too many minutes')
    elif mins < 0:
        raise Exception('negative minutes')
    else:
        return mins

# number of minutes that have elapsed since beginning of week until beginning of day d
def parse_day(d):
    if (d.lower()) in days:
        return (days.index(d.lower())) * MINS_PER_DAY
    else:
        raise Exception("not a day")

# takes time as string, returns hours in terms of minutes, 
# works for military or otherwise
def parse_hours(s):
    temp = (s.replace(' ','')).split(':')
    if len(temp) is not 2:
        raise Exception("illformed time: need exactly one ':'")
    hours = 0
    try:
        hours = int(temp[0])
    except Exception:
        raise Exception('illformed time: strange hours')
    #mins= int(filter(lambda x: x.isdigit(), temp[-1]))
    m = ''.join(list(filter(lambda x: not x.isdigit(), temp[-1])))
    if hours > HOURS_PER_DAY:
        raise Exception('time > 24 hours')
    elif hours < HOURS_PER_DAY and hours > NOON:
        if m != "":
            raise Exception("'can't mix military time and am/pm")
    elif m != "PM" and m != "":
        raise Exception('extra characters')
    elif hours == HOURS_PER_DAY:
        hours = 0
    elif hours == NOON and m == "AM":
        hours = 0
    elif hours < 0:
        raise Exception('negative time')
    #error_exit("negative time")
    elif m == "PM":
        if hours != NOON:
            hours += NOON
    hours *= MINS_PER_HOUR
    return hours

# jank helper function
def mins_to_time(n):
    m = "AM"
    temp = int(n) % MINS_PER_WEEK
    #flash('its this')
    dt = days[temp // MINS_PER_DAY]
    hours = temp % MINS_PER_DAY
    hours = hours // MINS_PER_HOUR
    if hours >= NOON:
        m = "PM"
    hours %= NOON
    if hours == 0:
        hours = NOON
    mins = temp % MINS_PER_HOUR
    mins = str(mins)
    if len(mins) == 1:
        mins = "0"+mins
    return (dt.title(), str(hours)+':'+mins+m)

def end_day_validate(sd, st, et):
    sth, stm = parse_hours(st), parse_mins(st)
    eth, etm = parse_hours(et), parse_mins(et)

    sm, em = sth + stm, eth + etm

    diff = em - sm

    if diff == 0:
        raise Exception('intervals of length 0 not allowed, please remove from schedule')
    next_day = (diff < 0)
    i = days.index(sd.lower())
    if next_day:
        return days[(i + 1) % 7]
    else:
        return days[i % 7]

def military_to_standard(mt):
    h, m= int(mt.split(':')[0]), mt.split(':')[1]

    if h == 0:
        return '12:'+m+'AM'
    elif h == 12:
        return '12:'+m+'PM'
    elif h > 12:
        return str(h % 12)+':'+m+'PM'
    elif h < 12:
        return str(h)+':'+m+'AM'

def sanitize_timestr(sd, st, ed, et):
    return (sd.title(), military_to_standard(st), ed.title(), military_to_standard(et))

# does the work of timestr_to_minutes
# could be public too tbh, this is useful
def to_min_interval(t):
    #flash('to_min_interval')
    (ds, s, de, e) = t
    shour, ehour = parse_hours(s), parse_hours(e)
    sday, eday = parse_day(ds), parse_day(de)
    sm, em = parse_mins(s), parse_mins(e)
    sm, em = sm + shour + sday, em + ehour + eday

    if sday == 8640 and eday == 0:
        em += MINS_PER_WEEK

    diff = em - sm
    if diff is 0:
        raise Exception('intervals of length 0 not allowed, please remove from schedule')
    elif diff < 0:
        raise Exception('negative interval')

    return sm, em

# takes list of tuples (sd, st, ed, et)
def timestr_to_minutes(tx):
    #flash('in timestr_to_minutes')
    return list(map(to_min_interval, tx))

# takes list of tuples (st, et) both in minutes from start of week
def minutes_to_timestr(l):
    unzipped = list(map(list, zip(*l)))
    sx, ex = [], []
    if unzipped:
        sx, ex = unzipped[0], unzipped[-1]
    temp = zip(list(map(mins_to_time, sx)), list(map(mins_to_time, ex)))
    return list(map(lambda x: (x[0][0], x[0][1], x[1][0], x[1][1]), temp))

#x = timestr_to_minutes([('monday', '1:00', 'monday', '12:00pm')])
#print(x)
