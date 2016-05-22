### Based on CloudBot's Weather Underground plugin

import requests


## some constants

google_base = 'https://maps.googleapis.com/maps/api/'
geocode_api = google_base + 'geocode/json'

wunder_api = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"

# Change this to a ccTLD code (eg. uk, nz) to make results more targeted towards that specific country.
# <https://developers.google.com/maps/documentation/geocoding/#RegionCodes>
bias = "US"

# Add your Google Dev key here
dev_key = ""

# Add your Wunderground API key here
wunder_key = ""

# Whether you want output in F and MPH, in C and km/h, or both
# possible values: "f", "c", "both"
units = "f"


## some necessary helper functions

def setup():
    return WeatherPlugin()

def check_status(status):
    if status == 'REQUEST_DENIED':
        return 'The geocode API is off in the Google Developers Console.'
    elif status == 'ZERO_RESULTS':
        return 'No results found.'
    elif status == 'OVER_QUERY_LIMIT':
        return 'The geocode API quota has run out.'
    elif status == 'UNKNOWN_ERROR':
        return 'Unknown Error.'
    elif status == 'INVALID_REQUEST':
        return 'Invalid Request.'
    elif status == 'OK':
        return None

def find_location(channel, location, cardinal):
    params = {"address": location, "key": dev_key}
    if bias:
        params['region'] = bias
    
    json = requests.get(geocode_api, params=params).json()

    error = check_status(json['status'])
    if error:
        cardinal.sendMsg(channel, "An error occurred: \x02{}\x02".format(error))
        return None
    else:
        return json['results'][0]['geometry']['location']


## main class

class WeatherPlugin(object):
    def get_weather(self, cardinal, user, channel, msg):
        if not wunder_key:
            cardinal.sendMsg(channel, "This command requires a Weather Underground API key.")
            return
        if not dev_key:
            cardinal.sendMsg(channel, "This command requires a Google Dev Console API key.")
            return

        try:
            location = msg.split(' ', 1)[1]
        except IndexError:
            cardinal.sendMsg(channel, "Syntax: .weather <location>")
            return

        try:
            location_data = find_location(channel, location, cardinal)
            if not location_data:
                return
        except IndexError:
            cardinal.sendMsg(channel, "An undefined error occurred.")
            return
                
        formatted_location = "{lat},{lng}".format(**location_data)
            
        url = wunder_api.format(wunder_key, formatted_location)
        
        response = requests.get(url).json()
            
        if response['response'].get('error'):
            cardinal.sendMsg(channel, "An error occurred: \x02{}\x02".format(response['response']['error']['description']))
            return

        forecast_today = response["forecast"]["simpleforecast"]["forecastday"][0]
        forecast_tomorrow = response["forecast"]["simpleforecast"]["forecastday"][1]
            
        weather_data = {
            "place": response['current_observation']['display_location']['full'],
            "conditions": response['current_observation']['weather'],
            "temp_f": response['current_observation']['temp_f'],
            "temp_c": response['current_observation']['temp_c'],
            "humidity": response['current_observation']['relative_humidity'],
            "wind_kph": response['current_observation']['wind_kph'],
            "wind_mph": response['current_observation']['wind_mph'],
            "wind_direction": response['current_observation']['wind_dir'],
            "today_conditions": forecast_today['conditions'],
            "today_high_f": forecast_today['high']['fahrenheit'],
            "today_high_c": forecast_today['high']['celsius'],
            "today_low_f": forecast_today['low']['fahrenheit'],
            "today_low_c": forecast_today['low']['celsius'],
            "tomorrow_conditions": forecast_tomorrow['conditions'],
            "tomorrow_high_f": forecast_tomorrow['high']['fahrenheit'],
            "tomorrow_high_c": forecast_tomorrow['high']['celsius'],
            "tomorrow_low_f": forecast_tomorrow['low']['fahrenheit'],
            "tomorrow_low_c": forecast_tomorrow['low']['celsius']
        }
            
        if units == "f":
            cardinal.sendMsg(channel, "{place} - \x02Current:\x02 {conditions}, {temp_f}F, Humidity: {humidity}, "
                             "Wind: {wind_mph}MPH from {wind_direction}, \x02Today:\x02 {today_conditions}, "
                             "High: {today_high_f}F, Low: {today_low_f}F. "
                             "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F, "
                             "Low: {tomorrow_low_f}F.".format(**weather_data))
            return
        elif units == "c":
            cardinal.sendMsg(channel, "{place} - \x02Current:\x02 {conditions}, {temp_c}C, Humidity: {humidity}, "
                             "Wind: {wind_kph}km/h from {wind_direction}, \x02Today:\x02 {today_conditions}, "
                             "High: {today_high_c}C, Low: {today_low_c}C. "
                             "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_c}C, "
                             "Low: {tomorrow_low_c}C.".format(**weather_data))
            return
        elif units == "both":
            cardinal.sendMsg(channel, "{place} - \x02Current:\x02 {conditions}, {temp_f}F / {temp_c}C, Humidity: {humidity}, "
                             "Wind: {wind_mph}MPH / {wind_kph}km/h from {wind_direction}, \x02Today:\x02 {today_conditions}, "
                             "High: {today_high_f}F / {today_high_c}C, Low: {today_low_f}F / {today_low_c}C. "
                             "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F / {tomorrow_high_c}C, "
                             "Low: {tomorrow_low_f}F / {tomorrow_low_c}C.".format(**weather_data))
            return
        else:
            cardinal.sendMsg(channel, "An error occurred: \x02An invalid unit discriminator has been set in the plugin file!\x02")
            return
    

    get_weather.commands = ['weather', 'w']
    get_weather.help = ["Retrieves the weather using the Weather Underground API.",
                        "Syntax: .weather <location>"]
