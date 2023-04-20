import data_gather as dg

# dg.save_meteo_stations()

date_range = dg.get_date_range("2023-01-01", "2023-03-19")

data = dg.get_station_data("Saint-Alban", date_range)
# print(data)













