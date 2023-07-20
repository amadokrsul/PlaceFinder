import googlemaps
import pandas as pd
import re
import pprint
import time

class PlaceSearch:
    global GOOGLE_API; GOOGLE_API = ''

    def __init__(self, API_key: str = None, maps_client = None) -> None:
        if type(API_key) is not str: raise TypeError("API Key has to be a string")
        
        self.maps_client = googlemaps.Client(API_key)

    def get_coordinates(self, location_query: str = None) -> str:
        if type(location_query) is not str: raise TypeError("Location query has to be a string specifying location")
        
        address = self.maps_client.geocode(location_query)
        lat, lng = address[0]['geometry']['location'].values()
        return str(lat) + ", " + str(lng)
        
    def get_businesses_id(self, coords: str = None, search_query: str = None, search_distance: int = None) -> list:
        if type(coords) is not str: raise TypeError("Coordinates have to be in 'latitude, longitude' string format")
        if type(search_query) is not str: raise TypeError("Search query has to be a string specifying search keywords")
        if type(search_distance) is not int: raise TypeError("Search distance has to be an integer specifying search radius in meters")

        businesses = []
        search = self.maps_client.places_nearby(keyword = search_query, location = coords, radius = search_distance)
        next_page_token = search['next_page_token']
        while next_page_token:
            for place in search['results']:
                businesses.append(place['place_id'])
            time.sleep(2)
            search = self.maps_client.places_nearby(keyword = search_query, location = coords, radius = search_distance, 
                                                    page_token = next_page_token)
            next_page_token = search.get('next_page_token', False)
        return businesses
        
    def convert_place_to_table(self, places: list = None) -> pd.DataFrame:
        if type(places) is not list: raise TypeError("Places has to be a list of place_id's")
        
        table = []
        params = ['name', 'website', 'formatted_address', 'formatted_phone_number']
        for id in places:
            place = self.maps_client.place(place_id = id, fields = params)
            results = place['result']
            if 'website' not in results: continue
            data = []
            for i in range(len(params)):
                data.append(results.get(params[i], ''))
            table.append(data)
        labels = ['Name', 'Website', 'Address', 'Phone Number']
        chart = pd.DataFrame(data = table, columns = labels)
        return chart
        

@staticmethod
def check_valid_location(coords: str):
    pattern = re.compile('^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$')
    return re.match(pattern, coords)

def main():
    client = PlaceSearch(API_key = GOOGLE_API)
    coordinates = input("Enter a location to perform the search in 'latitude, longitude' format or enter a place: ")
    if not check_valid_location(coordinates): 
        print("Input coordinates not valid. Performing search from place description: ")
        coordinates = client.get_coordinates(coordinates)

    query = input("Enter what places you wish to search for: ")
    distance = input("Enter the radius in which to perform the search (in meters): ")
    businesses = client.get_businesses_id(coords = coordinates, search_query = query, search_distance = int(distance))
    
    business_info = client.convert_place_to_table(businesses)
    business_info.to_csv('businesses.csv')


if __name__ == '__main__':
    main()


