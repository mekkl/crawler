
import bs4
import ast # https://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
import sys
import os
import requests
import re
import time
import datetime
from tqdm import tqdm
import json
from dateparser import parse
import argparse # https://docs.python.org/3/howto/argparse.html




## REPRESENT CLASS ATTRIBUTE start and epoch params!!!!  !!! 
## PARAMS: timeout ,start, epoch
## TODO: Change scrape_links() to class with attribute!!!!
def scrape_links(from_url, for_depth=0, all_links={'found': 0, 'total_runtime': 0, 'links':{}}, start=None, epoch=None):
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
    # regex_html not needed because of text/html Content-type value checker?
    # regex_html = re.compile(r"<(\"[^\"]*\"|'[^']*'|[^'\">])*>", re.IGNORECASE) # HTML elements

    # ---- Continue if depth >= 0 and if link doesn't already have been scraped ----
    if for_depth >= 0 and links.get('links', {}).get(from_url) is None: 
        links['links'].setdefault(from_url, []) # create list for new link key

        # ---- try, except block if requests raises exception ----
        try: 
            r = requests.get(from_url, timeout=(5, 5)) # TODO: make timeout a attribute of crawler class
            r.raise_for_status() # raise hvis status for get ikke er 'OK'

            # ---- Continue if response text matches HTML elements pattern (regex) ----
            # OBS: line below is for matching a regex up against the response content
            #if re.match(regex_html, r.text) is not None: 
            # OBS: line below is for matching a string up against the response header 'Content-type'
            if 'text/html' in r.headers['Content-type']:
                soup = bs4.BeautifulSoup(r.text, 'html5lib') # parse HTML
                a_tags = soup.find_all('a') # find all a tags
                
                for a_tag in a_tags:
                    url = a_tag.attrs.get('href', '')
                    url = url[:-1] if len(url) > 0 and url[-1] == '/' else url # remove '/' from the last position
                    
                    # ---- Continue if href value matches URL pattern (regex) ----
                    if re.match(regex_url, url) is not None: 
                        links['links'][from_url].append(url) # append found link to list
                        links['found'] = links.get('found', 0) + 1

                        epoch = datetime.datetime.now()
                        elapsed = epoch - start
                        links['total_runtime'] = elapsed.total_seconds()

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
        parser.add_argument('-j', '--json', help='data dump to JSON (param filename)')
        parser.add_argument('-p', '--py', help='data dump to .py module (param filename)')
        parser.add_argument("-d", "--depth", help="Crawler Depth", type=int)
        args = parser.parse_args()

        # ---- checking given args ----
        url = args.url
        json_file_name = args.json if args.json else None
        py_file_name = args.py if args.py else None
        depth = args.depth if args.depth else 0

        # ---- start crawler ----
        scraped_links = scrape_links(url, depth)

        # ---- handle result ----
        if json_file_name is not None:
            with open(f'{json_file_name}.json', 'w') as fp:
                json.dump(scraped_links, fp)
        if py_file_name is not None:
            with open(f'{py_file_name}.py', 'w') as fp:
                fp.write(f'SERIALIZED = {scraped_links}')
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
        if json_file_name is not None:
            with open(f'{json_file_name}.json', 'w') as fp:
                json.dump(scraped_links, fp)
        if py_file_name is not None:
            with open(f'{py_file_name}.py', 'w') as fp:
                fp.write(f'SERIALIZED = {scraped_links}')
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