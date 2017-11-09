import urllib3
from collections import OrderedDict
from bs4 import BeautifulSoup
import re

ALLMENUS_LINK = 'https://www.allmenus.com'
STATE = 'fl'

ALL_RESTAURANT_FILTER = '-/'
DELIVERY_FILTER = '-/?filters=filter_delivery'
ONLINE_FILTER = '-/?filters=filter_online'
BOTH_FILTER = '-/?filters=filter_online,filter_delivery'

FILTER_LIST = [ALL_RESTAURANT_FILTER, DELIVERY_FILTER, ONLINE_FILTER, BOTH_FILTER]

def get_soup_from_link(link):
    http = urllib3.PoolManager()
    page = http.request('GET', link)

    if page.status == 200:
        return BeautifulSoup(page.data, 'html.parser')
    else:
        return None


def get_cities_in_state(allmenus_state_link):
    soup = get_soup_from_link(allmenus_state_link)

    section_list_div = soup.find('div', {'class': 'city-urls s-col-xs-12'})
    cities = section_list_div.find_all('a')

    city_links = OrderedDict()

    for city in cities:
        matching_object = re.match('<a href="(.*)">(.*)</a>', str(city))
        city_links[matching_object.group(2)] = ALLMENUS_LINK + matching_object.group(1) #+ ALL_RESTAURANT_FILTER

    return city_links


def get_restaurants_for_city(link):
    restaurant_links = OrderedDict()
    for filter in FILTER_LIST:
        soup = get_soup_from_link(link + filter)

        #restaurant_list_div = soup.find_all('li', {'class': 'restaurant-list-item clearfix'})
        restaurant_list_div = soup.find_all('h4', {'class': 'name'})
        #return len(restaurant_list)
        #P.F. Chang's
        for restaurant in restaurant_list_div:
            matching_object = re.match('<.*id="(?P<id>.*)" href="(?P<link>.*)">.*</a>', str(restaurant))
            restaurant_links[matching_object.group('id')] = ALLMENUS_LINK + matching_object.group('link')

    print(len(restaurant_links))

city_links = get_cities_in_state(ALLMENUS_LINK + '/' + STATE)

#counter = 0
#for city in city_links.keys():
#    counter += get_restaurants_for_city(city_links[city])
#    print(counter)

#print(counter)

get_restaurants_for_city(city_links['Tampa'])
