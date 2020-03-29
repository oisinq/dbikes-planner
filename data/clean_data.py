import pandas as pd
from datetime import datetime, time
from os import path
from os import listdir
from os.path import isfile, join


def datetime_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second


def seconds_in_previous_days(t):
    return t.timetuple().tm_yday * 24 * 60 * 60


def nearest_time(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def category(current_available_bikes):
    if current_available_bikes == 0:
        return 'empty'
    elif current_available_bikes < 2:
        return 'very low'
    elif current_available_bikes < 5:
        return 'low'
    elif current_available_bikes < 10:
        return 'moderate'
    else:
        return "high"


def main():
    dictionary = {}
    my_data = pd.read_csv("weather.csv")

    # mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/data"
    # allfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv")]

    allfiles = ['North Circular Road.csv', 'Kevin Street.csv', 'Brookfield Road.csv', 'St James Hospital (Luas).csv', 'Lime Street.csv', 'Heuston Bridge (South).csv', 'York Street East.csv', 'Custom House.csv', 'Killarney Street.csv', 'Molesworth Street.csv', 'Grangegorman Lower (South).csv', 'Hatch Street.csv', 'Fitzwilliam Square East.csv', 'Bolton Street.csv', 'Hanover Quay.csv', 'Merrion Square South.csv', 'Heuston Station (Car Park).csv', 'Phibsborough Road.csv', 'James Street East.csv', 'Rothe Abbey.csv', 'Newman House.csv', 'Rathdown Road.csv', 'Christchurch Place.csv', 'James Street.csv', 'Cathal Brugha Street.csv', 'Fenian Street.csv', 'Wolfe Tone Street.csv', 'Dame Street.csv', 'Broadstone.csv', 'Herbert Street.csv', 'Heuston Bridge (North).csv', 'John Street West.csv', 'Mount Street Lower.csv', "St. Stephen's Green South.csv", 'Frederick Street South.csv', 'King Street North.csv', 'Ormond Quay Upper.csv', 'Grangegorman Lower (North).csv', 'Denmark Street Great.csv', 'York Street West.csv', 'Blackhall Place.csv', 'Market Street South.csv', 'Fownes Street Upper.csv', 'Chatham Street.csv', 'Custom House Quay.csv', 'Strand Street Great.csv', 'Grattan Street.csv', 'Hardwicke Place.csv', 'Harcourt Terrace.csv', 'Mount Brown.csv', 'High Street.csv', 'Deverell Place.csv', 'Wilton Terrace (Park).csv', 'City Quay.csv', 'Exchequer Street.csv', 'Francis Street.csv', 'Eccles Street.csv', "George's Lane.csv", 'Fitzwilliam Square West.csv', 'New Central Bank.csv', 'Convention Centre.csv', 'Sandwith Street.csv', 'Merrion Square East.csv', 'Golden Lane.csv', 'Jervis Street.csv', 'Grand Canal Dock.csv', 'Charlemont Street.csv', 'Pearse Street.csv', 'Hanover Quay East.csv', 'Collins Barracks Museum.csv', 'Clonmel Street.csv', 'Mountjoy Square West.csv', "North Circular Road (O'Connell's).csv", 'St. James Hospital (Central).csv', 'Wilton Terrace.csv', 'Leinster Street South.csv', 'Upper Sherrard Street.csv', 'Townsend Street.csv', 'Hardwicke Street.csv', 'Talbot Street.csv', 'Benson Street.csv', "Sir Patrick's Dun.csv", 'Georges Quay.csv', 'Avondale Road.csv', 'South Dock Road.csv', 'Blessington Street.csv', 'Herbert Place.csv', 'Excise Walk.csv', 'Greek Street.csv', 'Portobello Harbour.csv', 'Parkgate Street.csv', 'Smithfield North.csv', 'Princes Street.csv', 'Royal Hospital.csv', 'Emmet Road.csv', 'Heuston Station (Central).csv', 'Earlsfort Terrace.csv', 'Portobello Road.csv', 'Kilmainham Gaol.csv', 'Smithfield.csv', 'Charleville Road.csv', 'Western Way.csv', 'Grantham Street.csv', 'Oliver Bond Street.csv', "St. Stephen's Green East.csv", 'Parnell Street.csv', 'Barrow Street.csv', 'Guild Street.csv', 'Grangegorman Lower (Central).csv', 'Eccles Street East.csv', 'Merrion Square West.csv', 'Kilmainham Lane.csv', 'Mountjoy Square East.csv', 'Parnell Square North.csv', 'Buckingham Street Lower.csv', 'Mater Hospital.csv']

    for line in my_data.values:
        date = datetime.strptime(line[0], '%d-%b-%Y %H:%M')
        dictionary[date] = line

    for file in allfiles:
        my_data = pd.read_csv(file)
        f = open(f'./combined/{file}', 'w')

        f.write(
            "available_bike_stands,time_of_day,type_of_day,day_of_year,iso_date,temperature,relative_humidity,vapour_pressure,"
            "wind_speed,rain,sunshine,visibility,category\n")

        previous_number_of_bikes = 0

        for line in my_data.sort_values('last_update').values:
            available_bikes = line[4]
            epoch_time = line[5]

            entry_datetime = datetime.fromtimestamp(epoch_time / 1000)

            if is_time_between(time(0, 30), time(5, 0), entry_datetime.time()):
                continue

            weather_date = nearest_time(dictionary.keys(), entry_datetime)

            weather_line = dictionary[weather_date]

            day_index = entry_datetime.weekday()
            day_type = ''

            if day_index <= 4:
                day_type = 0
            else:
                day_type = 10

            f.write(f"{available_bikes},{datetime_to_seconds(entry_datetime)},{day_type},"
                    f"{entry_datetime.timetuple().tm_yday},{entry_datetime.isoformat()},{weather_line[4]},{weather_line[9]},"
                    f"{weather_line[8]},{weather_line[12]},{weather_line[2]},{weather_line[17]},{weather_line[18]},"
                    f"{category(available_bikes)}\n")

        print(f"Completed cleaning file {file}")

if __name__ == "__main__":
    main()