from bs4 import BeautifulSoup
import requests
from datetime import datetime
from getopt import getopt, GetoptError
import os, sys, re


def getUrl(year, day):
    return f'https://adventofcode.com/{year}/day/{day}'


def getResponse(url):
    response = requests.get(url, cookies={'session': os.getenv('SESSION_ID')})

    if response.status_code != 200:
        raise ValueError(f"Querying the url {url} for year {year} and day {day} resulted in status code "
                         f"{response.status_code} with the following text: {response.text}")

    return response


def getHtml(year, day):
    return getResponse(getUrl(year, day)).text


def getInput(year, day):
    return getResponse(getUrl(year, day) + '/input').text


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
    elif tag.name == 'a':
        tag.insert_before('[')
        tag.insert_after(f']({tag["href"]})')
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
        tag.unwrap()
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


def write(dir, content):
    if dir:
        os.makedirs(os.path.dirname(dir), exist_ok=True)

        with open(dir, 'w') as file:
            file.write(content)
    else:
        print(content)


def logUsage():
    print(f'Usage: {sys.argv[0]} [-y <year>] [-d <day>] [-o <output_dir>] [-s]')
    print('`-s` argument indicates whether the markdown should be printed or not. Only relevant when not indicating '
          'neither output_dir nor filename.')


def extractArguments():
    try:
        opts, args = getopt(sys.argv[1:], 'y:d:o:si', ['year=', 'day=', 'output=', 'save', 'input'])
    except GetoptError:
        logUsage()
        sys.exit(1)

    year = None
    day = None
    output = None
    explicitSave = False
    downloadInput = False

    for opt, arg in opts:
        if opt == '-h':
            logUsage()
            sys.exit(0)
        elif opt in ('-y', '--year'):
            year = int(arg)
        elif opt in ('-d', '--day'):
            day = int(arg)
        elif opt in ('-o', '--output'):
            output = arg
        elif opt in ('-s', '--save'):
            explicitSave = True
        elif opt in ('-i', '--input'):
            downloadInput = True

    if year is None:
        now = datetime.now()

        year = now.year

        if now.month != 12:
            # If at the current year it is not December, then go to the previous year
            year -= 1

    # Look in the current directory and retrieve the next day until a maximum if 25
    if day is None:
        folderSyntax = re.compile('^day-(\d+)$')

        prefix = (output if output else '')

        isValidDir = lambda dir: os.path.isdir(prefix + dir) and folderSyntax.match(dir)

        dirs = [int(folderSyntax.search(f).group(1)) for f in os.listdir(output) if isValidDir(f)]

        day = max(dirs, default=0) + 1

        if day > 25:
            raise ValueError(f'No day was provided as argument to the script. '
                             f'When trying to deduce the day, it got to day {day} which is not valid (maximum is 25). '
                             f'Take a look at the directory and check what is the last day that there is a directory.')

    file = None

    folderName = 'day-' + f'{day:02d}'

    if output or explicitSave:
        file = os.path.join(output if output else '.', folderName, 'README.md')

    input = None

    if downloadInput:
        input = os.path.join(output if output else '.', folderName, 'input.txt')

    return year, day, file, input


# JavaScript version: https://github.com/kfarnung/aoc-to-markdown
if __name__ == '__main__':
    year, day, fileDir, inputDir = extractArguments()

    markdown = getMarkdown(year, day)

    write(fileDir, markdown)

    if inputDir:
        write(inputDir, getInput(year, day))
