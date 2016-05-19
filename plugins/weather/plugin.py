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

# Whether you want output in F and MPH, in °C and km/h, or both
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

def find_location(channel, location):
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
            location_data = find_location(channel, location)
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
            cardinal.sendMsg(channel, "{place} - \x02Current:\x02 {conditions}, {temp_c}°C, Humidity: {humidity}, "
                             "Wind: {wind_kph}km/h from {wind_direction}, \x02Today:\x02 {today_conditions}, "
                             "High: {today_high_c}°C, Low: {today_low_c}°C. "
                             "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_c}°C, "
                             "Low: {tomorrow_low_c}°C.".format(**weather_data))
            return
        elif units == "both":
            cardinal.sendMsg(channel, "{place} - \x02Current:\x02 {conditions}, {temp_f}F / {temp_c}°C, Humidity: {humidity}, "
                             "Wind: {wind_mph}MPH / {wind_kph}km/h from {wind_direction}, \x02Today:\x02 {today_conditions}, "
                             "High: {today_high_f}F / {today_high_c}°C, Low: {today_low_f}F / {today_low_c}°C. "
                             "\x02Tomorrow:\x02 {tomorrow_conditions}, High: {tomorrow_high_f}F / {tomorrow_high_c}°C, "
                             "Low: {tomorrow_low_f}F / {tomorrow_low_c}°C.".format(**weather_data))
            return
        else:
            cardinal.sendMsg(channel, "An error occurred: \x02An invalid unit discriminator has been set in the plugin file!\x02")
            return
    

    get_weather.commands = ['weather', 'w']
    get_weather.help = ["Retrieves the weather using the Weather Underground API.",
                        "Syntax: .weather <location>"]


if False:'''
import urllib2
from xml.dom import minidom

WHERE_API_APP_ID = "MoToWJjdQX4XzV34ELXxh3MLG5x1cgBMiMrEuJ.0D_bohsdQlv5p7qzQXLgXmWID_zPRxFULW454h3"
WHERE_API_URL = "http://where.yahooapis.com/v1/places.q(%s);count=1?appid=" + WHERE_API_APP_ID
WHERE_API_NS = "http://where.yahooapis.com/v1/schema.rng"
WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?w=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

class WeatherPlugin(object):
    def get_weather(self, cardinal, user, channel, msg):
        try:
            location = msg.split(' ', 1)[1]
        except IndexError:
            cardinal.sendMsg(channel, "Syntax: .weather <location>")
            return

        try:
            url = WHERE_API_URL % urllib2.quote(location)
            dom = minidom.parse(urllib2.urlopen(url))
        except urllib2.URLError:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Where API. (URLError Exception occurred (#1).)")
        except urllib2.HTTPError:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Where API. (HTTPError Exception occurred (#1).)")
            return

        try:
            woeid = str(dom.getElementsByTagNameNS(WHERE_API_NS, 'woeid')[0].firstChild.nodeValue)
        except IndexError:
            cardinal.sendMsg(channel, "Sorry, couldn't find weather for \"%s\" (no WOEID)." % location)
            return

        try:
            url = WEATHER_URL % urllib2.quote(woeid)
            dom = minidom.parse(urllib2.urlopen(url))
        except urllib2.URLError:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Weather API. (URLError Exception occurred (#2).)")
            return
        except urllib2.HTTPError:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Weather API. (HTTPError Exception occurred (#2).)")
            return

        try:
            ylocation = dom.getElementsByTagNameNS(WEATHER_NS, 'location')[0]
            yunits = dom.getElementsByTagNameNS(WEATHER_NS, 'units')[0]
            ywind = dom.getElementsByTagNameNS(WEATHER_NS, 'wind')[0]
            yatmosphere = dom.getElementsByTagNameNS(WEATHER_NS, 'atmosphere')[0]
            ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]

            location_city = str(ylocation.getAttribute('city'))
            location_region = str(ylocation.getAttribute('region'))
            location_country = str(ylocation.getAttribute('country'))

            current_condition = str(ycondition.getAttribute('text'))
            current_temperature = str(ycondition.getAttribute('temp'))
            current_humidity = str(yatmosphere.getAttribute('humidity'))
            current_wind_speed = str(ywind.getAttribute('speed'))

            units_temperature = str(yunits.getAttribute('temperature'))
            units_speed = str(yunits.getAttribute('speed'))
            
            if units_temperature == "F":
                units_temperature2 = "C"
                current_temperature2 = str(int((float(current_temperature) - 32) * float(5)/float(9)))
            else:
                units_temperature2 = "F"
                current_temperature2 = str(int(float(current_temperature) * float(9)/float(5) + 32))

            location = location_city
            if location_region:
                location += ", " + location_region
            if location_country:
                location += ", " + location_country

            cardinal.sendMsg(channel, "[ %s | %s | Temp: %s %s (%s %s) | Humidity: %s%% | Winds: %s %s ]" %
                                                                                   (location,
                                                                                    current_condition,
                                                                                    current_temperature, units_temperature,
                                                                                    current_temperature2, units_temperature2,
                                                                                    current_humidity,
                                                                                    current_wind_speed, units_speed))
        except IndexError:
            cardinal.sendMsg(channel, "Sorry, couldn't find weather for \"%s\"." % location)
            return

    get_weather.commands = ['weather', 'w']
    get_weather.help = ["Retrieves the weather using the Yahoo! weather API.",
                        "Syntax: .weather <location>"]

def setup():
    return WeatherPlugin()
'''
