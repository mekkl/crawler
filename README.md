
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

### positional arguments:

- `url`  -  Starting point for crawler

### optional arguments: 
* `-h, --help`  -  show this help message and exit
* `-j, --json`  -  JSON dump filename
* `-d, --depth` -  Crawler depth (default = 0)
