
## Python Webcrawler project
`url` to use: `http://www.pythex.org`

## Dependencies
[tqdm](https://github.com/tqdm/tqdm): A fast, extensible progress bar for Python and CLI
```
$ pip install argparse
```

[argparse](https://docs.python.org/3/library/argparse.html): Parser for command-line options, arguments and sub-commands¶
```
$ pip install argparse
```

[ast](https://docs.python.org/3/library/ast.html): Process trees of the Python abstract syntax grammar.
```
$ pip install ast
```

[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): library for pulling data out of HTML and XML files.
```
$ pip install bs4
```

[requests](http://docs.python-requests.org/en/master/): Requests is the only Non-GMO HTTP library for Python, safe for human consumption.
```
$ pip install requests
```

## Usage
```
$ python crawler.py [-h] [-j] [-d] url
```

### Example
```
$ python crawler.py -j file_name -d 2 http://www.pythex.org
```


### positional arguments:
- `url`  -  Starting point for crawler

### optional arguments: 
* `-h, --help`  -  show this help message and exit
* `-j, --json`  -  JSON dump filename
* `-d, --depth` -  Crawler depth (default = 0)

## Issues

### Crawler depth
The crawler finds more links for depth 2 than 3. This should, maybe, not be the case since the crawler would dig deeper and therefore find more links.

Fix?: The crawler ignores to click link if the crawler already have clicked it (checks the internal dictionary `all_links` if dict contains the link as a key). Check, via the .json test files, if a link (key), contains a longer list, of links, than the other. If that is the case, maybe the crawler, which goes to a deeper depth, clicks on a link from a different site than the smaller depth crawler, and therefore gets shown a different amount of links.