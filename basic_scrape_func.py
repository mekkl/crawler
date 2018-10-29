import bs4
import requests
import re
from tqdm import tqdm
from dateparser import parse

def scrape_no_events(url):
    """
    Find amount of pages to parse from the entry html page
    
    returns:
        An integer with the amount of events
    """
    r = requests.get(url)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html5lib')

    tables = soup.select('table')

    # The second table of depth three holds the amount of events
    depth3 = [t for t in tables if len(t.find_parents('table')) == 3]
    # The only bold element holds the amount of events
    event_str = depth3[1].select('b')[0].text.splitlines()[0]

    reg_exp = r'Showing .+ of (?P<events>\d+)'
    m = re.search(reg_exp, str(event_str))
    no_events = int(m.group('events'))
    
    return no_events

def scrape_events_per_page(url):
    """
    returns:
        A list of tuples of strings holding title, place, date, and price
        for concerts in Copenhagen scraped from Kulturnaut.dk
    """
    r = requests.get(url)
    r.raise_for_status()

    soup = bs4.BeautifulSoup(r.text, 'html5lib')
    event_cells = soup.find_all('td', {'width': '100%', 'valign' : 'top'})
    scraped_events_per_page = []
    for event_cell in event_cells:
        try:
            title = event_cell.find('b').text
            spans = event_cell.find_all('span')
            place = spans[1].text
            try:
                date, price = spans[0].text.splitlines()
            except ValueError as e:
                date = spans[0].text.splitlines()[0]
                price = ''
        except Exception as e:
            print(e)
            
        scraped_events_per_page.append((title, place, date, price))
        
    return scraped_events_per_page


def get_dates_and_prices(scraped_events):
    """
    Cleanup the data. Get price as integer and date as date.
    
    returns:
        A two-element tuple with a datetime representing the start 
        time of an event and an integer representing the price in Dkk.
    """

    price_regexp = r"(?P<price>\d+)"

    data_points = []

    for event_data in tqdm(scraped_events):
        title_str, place_str, date_str, price_str = event_data
        
        if 'Free admission' in price_str:
            price = 0
        else:
            m = re.search(price_regexp, price_str)
            try:
                price = int(m.group('price'))
            except:
                price = 0

        date_str = date_str.strip().strip('.')
        if '&' in date_str:
            date_str = date_str.split('&')[0]
        if '-' in date_str:
            date_str = date_str.split('-')[0]
        if '.' in date_str:
            date_str = date_str.replace('.', ':')
        
        date = parse(date_str)
        if date:
            data_points.append((date, price))
            
    return data_points