from bs4 import BeautifulSoup
import requests
from datetime import datetime
from getopt import getopt, GetoptError
import os, sys, re


def getUrl(year, day):
    return f'https://adventofcode.com/{year}/day/{day}'


def getHtml(year, day):
    url = getUrl(year, day)

    response = requests.get(url, cookies={'session': os.getenv('SESSION_ID')})

    if response.status_code != 200:
        raise ValueError(f"Querying the url {url} for year {year} and day {day} resulted in status code "
                         f"{response.status_code} with the following text: {response.text}")

    return response.text


# Simplification of https://github.com/dlon/html2markdown/blob/master/html2markdown.py
def htmlTagsToMarkdown(tag, isFirstArticle):
    children = tag.find_all(recursive=False)

    if tag.name != 'code':
        for child in children:
            htmlTagsToMarkdown(child, isFirstArticle)

    if tag.name == 'h2':
        style = '#' if isFirstArticle else '##'
        tag.insert_before(f'{style} ')
        tag.insert_after('\n\n')
        tag.unwrap()
    elif tag.name == 'p':
        tag.insert_after('\n')
        tag.unwrap()
    elif tag.name == 'em':
        style = '**' if tag.has_attr('class') and tag['class'] == 'star' else '*'
        tag.insert_before(style)
        tag.insert_after(style)
        tag.unwrap()
    elif tag.name == 'span':
        tag.insert_before('*')
        tag.insert_after('*')
        tag.unwrap()
    elif tag.name == 'ul':
        tag.unwrap()
    elif tag.name == 'li':
        tag.insert_before(' - ')
        tag.insert_after('\n')
    elif tag.name == 'code':
        if '\n' in tag.text:
            tag.insert_before('```\n')
            tag.insert_after('\n```')
        else:
            tag.insert_before('`')
            tag.insert_after('`')
        tag.unwrap()
    elif tag.name == 'pre':
        tag.insert_before('')
        tag.insert_after('\n')
        tag.unwrap()
    elif tag.name == 'article':
        pass
    else:
        raise ValueError(f'Missing condition for tag: {tag.name}')


def getMarkdown(year, day):
    soup = BeautifulSoup(getHtml(year, day), features="html.parser")

    articles = soup.body.main.findAll('article', recursive=False)
    markdown = ''

    for i, article in enumerate(articles):
        htmlTagsToMarkdown(article, i == 0)
        markdown += ''.join([tag.string for tag in article.contents])

    return markdown


def logUsage():
    print(f'Usage: {sys.argv[0]} [-y <year>] [-d <day>]')


def extractArguments():
    try:
        opts, args = getopt(sys.argv[1:], 'y:d:', ['year=', 'day='])
    except GetoptError:
        logUsage()
        sys.exit(1)

    year = None
    day = None

    for opt, arg in opts:
        if opt == '-h':
            logUsage()
            sys.exit(0)
        elif opt in ('-y', '--year'):
            year = arg
        elif opt in ('-d', '--day'):
            day = arg

    if year is None:
        now = datetime.now()

        year = now.year

        if now.month != 12:
            # If at the current year it is not December, then go to the previous year
            year -= 1

    # Look in the current directory and retrieve the next day until a maximum if 25
    if day is None:
        folderSyntax = re.compile('^day-(\d){1,2}$')

        dirs = [int(folderSyntax.search(f).group(1)) for f in os.listdir() if os.path.isdir(f) and folderSyntax.match(f)]

        day = max(dirs, default=0) + 1

        if day > 25:
            raise ValueError(f'No day was provided as argument to the script. '
                             f'When trying to deduce the day, it got to day {day} which is not valid (maximum is 25). '
                             f'Take a look at the directory and check what is the last day that there is a directory.')
            sys.exit(1)

    return year, day


# JavaScript version: https://github.com/kfarnung/aoc-to-markdown
if __name__ == '__main__':
    year, day = extractArguments()

    markdown = getMarkdown(year, day)
