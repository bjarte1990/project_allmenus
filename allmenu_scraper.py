import urllib3
from collections import OrderedDict
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import html

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

    return restaurant_links


def get_restaurant_details(links):
    headers = ['Location ID','Name','Address', 'City', 'State', 'Zip', 'Type', 'OverallRating', 'PriceLevel', 'PhoneNumber',
               'Website', 'GooglePlacesUrl', 'Lat', 'Lng', 'SearchTerm','Cuisine', 'Menu Section',
               'Dish Name', 'Description', 'Price', 'Extras', 'Extras Cost', 'Open Times', 'Close times',
               'Delivery', 'Reservations', 'Vegetarian', 'Spicy']
    restaurant_df = pd.DataFrame(columns=headers)
    id = 1
    for link in links:
        print('%d/%d' % (id, len(link)))
        try:
            soup = get_soup_from_link(link)
            order_grubhub = soup.find('a', {'class': 'center-button order-button-header'})
            order_seamless = soup.find('a', {'class': 'red-button order-button-header seamless-link'})
            data_string = html.unescape(str(soup.find('script', {'type': 'application/ld+json'}).contents[0]))
            to_escape = re.findall(':\"(.+\".+)\"[,]*\n', data_string)
            for s in to_escape:
                data_string = data_string.replace(s, s.replace('"', ''))
            json_data = json.loads(data_string, strict=False)

            if order_grubhub or order_seamless:
                online_order = 'yes'
            else:
                online_order = ''
            name = json_data['name']
            address = json_data['address']['streetAddress']
            city = json_data['address']['addressLocality']
            state = json_data['address']['addressRegion']
            zip = json_data['address']['postalCode']
            type = json_data['@type']
            price_level = json_data['priceRange']
            phone_number = json_data['telephone']
            website = ''
            google_places_url = ''
            lat = json_data['geo']['latitude']
            long = json_data['geo']['longitude']
            searchterm = json_data['servesCuisine']
            cousine = json_data['servesCuisine']
            open_times = json_data['openingHours']
            menu_list = []
            for menuSection in json_data['hasMenu']:
                for entry in menuSection['hasMenuSection']:
                    try:
                        menu = entry['hasMenuItem']
                        for dish in menu:
                            if 'vegetarian' in entry['name'].lower() or 'vegetarian' in dish['name'].lower() \
                                    or 'vegetarian' in dish['description'].lower() \
                                    or 'vegan' in entry['name'].lower() or 'vegan' in dish['name'].lower() \
                                    or 'vegan' in dish['description'].lower() :
                                vegetarian = 'yes'
                            else:
                                vegetarian = 'no'

                            if 'spicy' in entry['name'].lower() \
                                    or 'spicy' in dish['name'].lower() \
                                    or 'spicy' in dish['description'].lower():
                                spicy = 'yes'
                            else:
                                spicy = 'no'

                            if 'offers' in dish:
                                menu_list.append((entry['name'], dish['name'], dish['description'],
                                                  dish['offers'][0]['Price'], vegetarian, spicy))
                            else:
                                menu_list.append((entry['name'], dish['name'], dish['description'],
                                                  '', vegetarian, spicy))

                    except KeyError:
                        continue

            for dish in menu_list:
                row = [id,name,address,city,state,zip,type,'',price_level,
                                                phone_number,website,google_places_url,lat,long,
                                                ','.join(searchterm),','.join(cousine),dish[0],
                                                dish[1],dish[2],dish[3],'','',open_times,'',online_order,'',
                                                dish[4],dish[5]]
                restaurant_df = restaurant_df.append(pd.DataFrame(columns=restaurant_df.columns,data=[row]))
            id += 1
        except Exception as e:
            print(link)
            print(e)
    return restaurant_df

city_links = get_cities_in_state(ALLMENUS_LINK + '/' + STATE)

#counter = 0
restaurant_links = {}
for city in city_links.keys():
    print(city)
    restaurant_links.update(get_restaurants_for_city(city_links[city]))


#restaurant_links = get_restaurants_for_city(city_links['Tampa'])
restaurant_df = get_restaurant_details(list(restaurant_links.values()))
restaurant_df.to_excel('restaurants.xlsx', index=False)

#restaurant_df = get_restaurant_details(['https://www.allmenus.com/fl/tampa/46455-panera-bread/menu/'])

#print(restaurant_df)