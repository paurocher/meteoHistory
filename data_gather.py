"""
Graph:
    Graph of temperatures, precip, ... of a given meteo station
    - Can select several stations and display them all in the same graph with
    different colors.

Favorites:
    List of favorite meteo stations in list or map mode.

Map:
    Map with all available meteo stations.
    - Button for all stations.
    - Button for only favorite stations.
    - Drop a pin and list closest meteo stations ordered by distance.

Alarm:
    Will warn the user when temperatures of a given meteo station are between
    a given range during a given time. For example if temps for station XXX are
    below 10C during 5 days.
"""

"""HOW IT WORKS
1. Presentation page shows all available stations by name.
This is grabbed from a json file that stores {name: {idNumber, link, lat, long,
altitude}. The file has a dat_created key as well.
If the file doesn't exist it is generated. There is a button to refresh the 
stations list.
A calendar set to today's date lets us select a date range.

2. When a button is pressed, a new page shows the graph of the temperatures for
the set date range. 
"""

import bs4 as bs
import urllib.request
import datetime
import re
import json
import os
from pprint import pprint as pp


METEO_STATIONS_DUMP = "/Users/methodlocaluser/PycharmProjects/meteoHistory/meteo_stations_dump.json"

def save_meteo_stations():
    """Saves all meteo stations into a json file."""

    print("Getting meteo stations ...")
    # root page for all meteo stations for the current date
    site_address = """http://www.environnement.gouv.qc.ca/climat/donnees/OQtableau.asp?date_selection={}""".format(datetime.date.today())
    soup = bs.BeautifulSoup(urllib.request.urlopen(site_address),
                            features="html.parser")
    meteo_stations_names = soup.findAll("td", {"class": "station"})


    meteo_stations = {"date_created" : str(datetime.date.today())}
    link_root = "http://www.environnement.gouv.qc.ca/climat/donnees/"
    for i in meteo_stations_names:
        try:
            link = link_root + i.find("a").get("href")

            # grabs lat, long and alt
            soup = bs.BeautifulSoup(urllib.request.urlopen(link),
                                    features="html.parser")
            rows = soup.find("div", {"id": "contenu"}).find("table").findAll("tr")

            location = []
            for r_count, row in enumerate(rows):
                for count, col in enumerate(row.find_all("td")):
                    if r_count == 0 and count == 1:
                        location.append(col.text.encode("ascii", "ignore").decode("utf-8", "ignore"))
                        # location.append(col.text.replace("\xa0", ""))
                    if count == 3 and col.text != "\xa0":
                        location.append(col.text.encode("ascii", "ignore").decode("utf-8", "ignore"))
                        # location.append(col.text.replace("\xa0", ""))

            cle = re.findall("cle=(\d+)&date", link)
            if cle:
                cle = cle[0]
            meteo_stations[i.find("a").text] = {"cle": cle,
                                                "link": link,
                                                "lat": location[1],
                                                "long": location[2],
                                                "alt": location[3]}
        except AttributeError:
            pass

    with open(METEO_STATIONS_DUMP, "w") as file:
        json.dump(meteo_stations, file, ensure_ascii=False, indent=4)

    print("Found {} meteo stations in Quebec province.".format(len(meteo_stations)-1))




def get_station_data(station, dates):
    """Gets all data of a station for a given period. If the json file does not
    exist it creates it.

    :param station: str or int: station name or IDNumber
    :param date: what comes out of "get_date_range" function:
                    list with: - list of tuples
                               - list of dates
    :return: list of dicts: [{year, month, day, maxTemp, averageTemp, minTemp,
                              mmRain, mmTotalRain, cmSnow, cmSnowOnGround}]
    """

    # check if json file exists
    if not os.path.exists(METEO_STATIONS_DUMP):
        save_meteo_stations()

    with open (METEO_STATIONS_DUMP, "r") as file:
        stations = json.load(file)

    year_month = dates[0]
    data = []
    # print(year_month)
    for ym in year_month:
        site_address = re.sub("\d\d\d\d-\d\d-\d\d", "-".join(ym)+"-01", stations[station]["link"])
        # print(site_address)

        soup = bs.BeautifulSoup(urllib.request.urlopen(site_address),
                                features="html.parser")
        rows = soup.find("div", {"id": "contenu"}).findAll("table")[1].findAll("tr")
        # print(rows)

        period = soup.find("div", {"id": "contenu"}).findAll("table")
        period = period[0].findAll("tr")[2].find_all("td")[1].text.split("\xa0")
        # print(ym)
        # data for temps, rain, snow.

        for tr in rows:
            td = tr.find_all("td")

            row = [i.text.encode("ascii", "ignore").decode("utf-8", "ignore") for i in td]
            for char in ["\n", "\r", "\t", "\xa0"]:
                row = [i.replace(char, "") for i in row]

            if row and row[0] in ["{:02d}".format(i) for i in range(1, 32)]:
                # print(row)
                headers = {}
                headers["Année"] = period[1]
                headers["Mois"] = period[0]
                headers["Jour"] = row[0]
                headers["TempMaxC"] = row[1]
                headers["TempMoyC"] = row[3]
                headers["TempMinC"] = row[5]
                headers["PrecipPluieMm"] = row[8]
                headers["PrecipPluieTotalMm"] = row[10]
                headers["PrecipNeigeCm"] = row[12]
                headers["PrecipNeigeAuSolCm"] = row[14]
                data.append(headers)

    pp(data)


def get_date_range(start, end):
    """Returns list of consecutive years, months and days in a date range.

    :param start: str: start date : "2020-11-01"
    :param end: str: end date: "2021-01-06"
    :return: list with - tuple of year/month pairs
                       - list of lists: [[2020, 11, 01], [2020, 11, 02], ...
                                        ..., [2021, 01, 06]]
    """

    months = ["janvier", "février", "mars", "avril", "mai", "juin",
              "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    try:
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    except ValueError:
        print("Start date seems wrong")
        return
    try:
        end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        print("End date seems wrong")
        return

    if start > end:
        print("Later date should go first, earlier date last.")
        return

    mini_date_list = []
    mini_date_set = set()
    step = datetime.timedelta(days=1)
    while start <= end:
        start_split = start.strftime('%Y-%m-%d').split("-")
        mini_date_list.append(start_split)
        mini_date_set.add((start_split[0], start_split[1]))
        start += step

    return [sorted([i for i in mini_date_set]), mini_date_list]
    # return mini_date_list


def get_json_info(request):
    with open (METEO_STATIONS_DUMP, "r") as file:
        stations = json.load(file)

    if request == "date_created":
        return stations["date_created"]

    elif request == "stations":
        return list(stations)[1:]

# save_meteo_stations()
# date_range = get_date_range("2020-11-29", "2021-1-6")
# get_station_data("Saint-Alban", date_range)
# pp(date_range)
