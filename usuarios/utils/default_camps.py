import random
import datetime
import datetime
from django.utils import timezone

def random_name():
    caracteres = (
        'a',
        'b',
        'c',
        'd',
        'e',
        'f',
        'g',
        'h',
        'i',
        'j',
        'k',
        'l',
        'm',
        'n',
        'o',
        'p',
        'q',
        'r',
        's',
        't',
        'u',
        'w',
        'y',
        'z',
        'v',
        'v',
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '!',
        '@',
        '#',
        '$',
        '&',
        '_',
        '=',
        '-',
        '+',
        '',
    )

    name = list()

    for i in range(254):
        name.append(random.choice(caracteres))
    name = "".join(name)

    return name


def get_time():
       
    return datetime.datetime.now()

def getDifference(gerated_access_token,interval = "hrs"):
    
    then=str(gerated_access_token)[:-6]
    now=(str(timezone.now())[:-13])
    print(then)
    print(now)


    

    then =(
                int(then[0:4]),
                int(then[5:7])  ,
                int(then[8:10])  ,
                int(then[11:13]),
                int(then[14:16]),
                int(then[17:19])
    )
    now =(
                int(now[0:4]),
                int(now[5:7])  ,
                int(now[8:10])  ,
                int(now[11:13]),
                int(now[14:16]),
                int(now[17:19])
    )
    print(then)
    print(now)


    then = (datetime.datetime(
                then[0],then[1],then[2],
                then[3],then[4],then[5]
                )
    )
    now = (datetime.datetime(
                now[0],now[1],now[2],
                now[3],now[4],now[5]
                )
    )
            
    duration =  now-then
    duration_in_s = duration.total_seconds() 
    
    #Date and Time constants
    yr_ct = 365 * 24 * 60 * 60 #31536000
    day_ct = 24 * 60 * 60 			#86400
    hour_ct = 60 * 60 					#3600
    minute_ct = 60 
    
    def yrs():
      return divmod(duration_in_s, yr_ct)[0]

    def days():
      return divmod(duration_in_s, day_ct)[0]

    def hrs():
      return divmod(duration_in_s, hour_ct)[0]

    def mins():
      return divmod(duration_in_s, minute_ct)[0]

    def secs(): 
      return duration_in_s
    
    return {
        'yrs': int(yrs()),
        'days': int(days()),
        'hrs': int(hrs()),
        'mins': int(mins()),
        'secs': int(secs())
    }[interval]




