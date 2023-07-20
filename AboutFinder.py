from urllib.parse import urlparse
from googleapiclient.discovery import build
import csv
import validators
import os
import pprint

class AboutFinder:
    
    def __init__(self, business_csv: str = None, business_links: list = None) -> None:
        if not os.path.isfile(business_csv): raise ValueError("Business_csv must be a string path")
        
        business_list = AboutFinder.read_csv(business_csv)
        self.names = []
        try:
            AboutFinder.validate_urls(business_links)
            for link in business_links:
                parsed = urlparse(link)
                self.names.append(parsed.hostname)
        except (ValueError, TypeError):
            do_search = input('Input business links are not valid, do you want to perform search from saved business list? (Y/n) ')
            if do_search == 'Y':
                for b in business_list:
                    parsed = urlparse(b[2])
                    self.names.append(parsed.hostname)
            else: 
                print("Goodbye!")            
                
    @staticmethod
    def read_csv(business_list: str = None) -> list:
        data = []
        with open(business_list, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                data.append(row)
        return data
                
    @staticmethod
    def validate_urls(links: list = None) -> bool:
        if type(links) is not list: raise TypeError("Links parameter has to be a list of home page URLs")
        
        for link in links:
            if not validators.url(link): return ValueError("Links parameter must include valid links")
        return True
            
    def find_about_links(self) -> list:
        if type(self.names) is not list: raise TypeError("Business names parameter has to be a list")
        
        country = input("From which country do you want the results? (country code) ")
        
        web_client = build("customsearch", 'v1', developerKey = '').cse()
        websites = []
        for names in self.names:
            html = web_client.list(
                q = "about" + " " + names,
                gl = country, 
                cx = "").execute()
            link = html['items'][0]['link']
            websites.append(link)
        pprint.pprint(websites)
            
def main():
    finder = AboutFinder(business_csv = './businesses.csv')
    finder.find_about_links()
    
if __name__ == '__main__':
    main()
    
