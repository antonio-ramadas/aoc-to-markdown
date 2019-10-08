from bs4 import BeautifulSoup
import requests
from getopt import getopt, GetoptError
import os, sys


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


# JavaScript version: https://github.com/kfarnung/aoc-to-markdown
if __name__ == '__main__':
    try:
        opts, args = getopt(sys.argv[1:], 'y:d:', ['year=', 'day='])
    except GetoptError:
        print(f'Usage: {sys.argv[0]} -y <year> -d <day>')
        sys.exit(1)

    year = 2019
    day = 1

    for opt, arg in opts:
        if opt == '-h':
            print(f'Usage: {sys.argv[0]} -y <year> -d <day>')
            sys.exit(0)
        elif opt in ('-y', '--year'):
            year = arg
        elif opt in ('-d', '--day'):
            day = arg

    print(getMarkdown(year, day))
