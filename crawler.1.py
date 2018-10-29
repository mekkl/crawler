
import bs4
import ast # https://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
import sys
import os
import requests
import re
import time
import datetime
import pprint
from selenium import webdriver
from tqdm import tqdm
import json
from dateparser import parse
import argparse # https://docs.python.org/3/howto/argparse.html


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

## REPRESENT CLASS ATTRIBUTE start and epoch params!!!!  !!! 
## PARAMS: timeout ,start, epoch
## TODO: Change scrape_links() to class with attribute!!!!
def scrape_links(from_url, for_depth=0, all_links={'found': 0, 'links':{}}, start=None, epoch=None):
    '''
        URL validation: https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
        HTML validation: http://www.mkyong.com/regular-expressions/how-to-validate-html-tag-with-regular-expression/
    '''
    if not bool(all_links['links']):
        start = datetime.datetime.now()

    # ---- copies the all_links arg ----
    backup = all_links.copy()
    links = all_links.copy()

    # ---- regex setup ----
    regex_url = re.compile( r'^(?:http|ftp)s?://', # http:// or https://
                        re.IGNORECASE) 
    regex_html = re.compile(r"<(\"[^\"]*\"|'[^']*'|[^'\">])*>", re.IGNORECASE) # HTML elements

    # ---- Continue if depth >= 0 and if link doesn't already have been scraped ----
    if for_depth >= 0 and links['links'].get(from_url) is None: 
        links['links'].setdefault(from_url, []) # create list for new link key

        # ---- try, except block if requests raises exception ----
        try: 
            r = requests.get(from_url, timeout=(5, 5)) # TODO: make timeout a attribute of crawler class
            r.raise_for_status() # raise hvis status for get ikke er 'OK'

            # ---- Continue if response text matches HTML elements pattern (regex) ----
            if re.match(regex_html, r.text) is not None: 
                soup = bs4.BeautifulSoup(r.text, 'html5lib') # parse HTML
                a_tags = soup.find_all('a') # find all a tags
                
                for a_tag in a_tags:
                    url = a_tag.attrs.get('href', '')
                    url = url[:-1] if len(url) > 0 and url[-1] == '/' else url # remove '/' from the last position

                    # ---- Continue if href value matches URL pattern (regex) ----
                    if re.match(regex_url, url) is not None: 
                        links['links'][from_url].append(url) # append found link to list
                        links['found'] = links['found'] + 1
                        
                        epoch = datetime.datetime.now()
                        elapsed = epoch - start

                        # ---- print to console ----
                        sys.stdout.write(f'\rnum_of_links: {links["found"]}, running_time (sec): {elapsed.total_seconds()}, for_depth: {for_depth}')
                        sys.stdout.flush()

                        # ---- RECURSIVE CALL ----
                        links = scrape_links(url, for_depth - 1, links, start) 

        except KeyboardInterrupt as e:
            '''
            should return latest stable version of the dict with links.
            happens to return found links (I think?) but not setting correct value of 'found'
            dict.found is set to 0.
            TODO: make the crawler raise the correct dict with correct found value
            '''
            raise KeyboardInterrupt(backup)

        except Exception as e:
            ''' 
            build exception dictionary to console print
            '''
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            e_dict = {'message': e, 'exc_type': exc_type, 'fname': fname, 'lineno': exc_tb.tb_lineno}
            print(f', exception: {e_dict}')
            return links # return if request didn't returned ok

    # ---- code for showing links which already have been found ----
    # elif for_depth >= 0 and links['links'].get(from_url) is not None: 
    #     print(f', already found: {from_url}')

    return links


if __name__ == '__main__':
    try:
        sys.stdout.write(f'') # console style

        # ---- program arg setup ----
        parser = argparse.ArgumentParser()
        parser.add_argument("url", help="Starting point for crawler")
        parser.add_argument('-j', '--json', help='JSON dump')
        parser.add_argument("-d", "--depth", help="Crawler Depth", type=int)
        args = parser.parse_args()

        # ---- checking given args ----
        url = args.url
        file_name = args.json if args.json else None
        depth = args.depth if args.depth else 0

        # ---- start crawler ----
        scraped_links = scrape_links(url, depth)

        # ---- handle result ----
        if file_name is not None:
            with open(f'{file_name}.json', 'w') as fp:
                json.dump(scraped_links, fp)
        else:
            print(scraped_links)
        print('') # console style
        print('') # console style
    
    except KeyboardInterrupt as e:
        '''
        Handles KeyboardInterrupt as an OK way of terminating the script.
        Therefor the found-links-dictionary will be presented to the user,
        as demanded 
        '''
        scraped_links = ast.literal_eval(str(e))
        print('') # console style
        print('') # console style
        print('catching crawler and handles found links...')

        # ---- handle result ----
        if file_name is not None:
            with open(f'{file_name}.json', 'w') as fp:
                json.dump(scraped_links, fp)
        else:
            print(scraped_links)

        print('') # console style
        print('') # console style
        sys.exit(0)
    except Exception as e:
        ''' 
        build exception dictionary to console print
        '''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        e_dict = {'message': e, 'exc_type': exc_type, 'fname': fname, 'lineno': exc_tb.tb_lineno}
        print(f', exception: {e_dict}')
        print('') # console style
        print('') # console style
        sys.exit(1)