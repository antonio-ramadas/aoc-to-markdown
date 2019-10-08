import os
import re
import sys
from datetime import datetime
from getopt import getopt, GetoptError

import requests
from bs4 import BeautifulSoup


def get_url(year, day):
    return f'https://adventofcode.com/{year}/day/{day}'


def get_response(url):
    response = requests.get(url, cookies={'session': os.getenv('SESSION_ID')})

    if response.status_code != 200:
        raise ValueError(f"Querying the url {url} resulted in status code {response.status_code} with the following "
                         f"text: {response.text}")

    return response


def get_html(year, day):
    return get_response(get_url(year, day)).text


def get_input(year, day):
    return get_response(get_url(year, day) + '/input').text


# Simplification of https://github.com/dlon/html2markdown/blob/master/html2markdown.py
def html_tags_to_markdown(tag, is_first_article):
    children = tag.find_all(recursive=False)

    if tag.name != 'code':
        for child in children:
            html_tags_to_markdown(child, is_first_article)

    if tag.name == 'h2':
        style = '#' if is_first_article else '##'
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


def get_markdown(year, day):
    soup = BeautifulSoup(get_html(year, day), features="html.parser")

    articles = soup.body.main.findAll('article', recursive=False)
    content = ''

    for i, article in enumerate(articles):
        html_tags_to_markdown(article, i == 0)
        content += ''.join([tag.string for tag in article.contents])

    return content


def write(directory, content):
    if directory:
        os.makedirs(os.path.dirname(directory), exist_ok=True)

        with open(directory, 'w') as file:
            file.write(content)
    else:
        print(content)


def print_usage():
    print(f'Usage: {sys.argv[0]} [-y <year>] [-d <day>] [-o <output_dir>] [-s]')
    print('`-s` argument indicates whether the markdown should be printed or not. Only relevant when not indicating '
          'neither output_dir nor filename.')


def extract_arguments():
    try:
        opts, args = getopt(sys.argv[1:], 'y:d:o:si', ['year=', 'day=', 'output=', 'save', 'input'])
    except GetoptError:
        print_usage()
        sys.exit(1)

    year = None
    day = None
    output = None
    explicit_save = False
    download_input = False

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit(0)
        elif opt in ('-y', '--year'):
            year = int(arg)
        elif opt in ('-d', '--day'):
            day = int(arg)
        elif opt in ('-o', '--output'):
            output = arg
        elif opt in ('-s', '--save'):
            explicit_save = True
        elif opt in ('-i', '--input'):
            download_input = True

    if year is None:
        now = datetime.now()

        year = now.year

        if now.month != 12:
            # If at the current year it is not December, then go to the previous year
            year -= 1

    # Look in the current directory and retrieve the next day until a maximum if 25
    if day is None:
        folder_syntax = re.compile('^day-(\\d+)$')

        prefix = (output if output else '')

        def is_valid_dir(directory):
            return os.path.isdir(prefix + directory) and folder_syntax.match(directory)

        dirs = [int(folder_syntax.search(f).group(1)) for f in os.listdir(output) if is_valid_dir(f)]

        day = max(dirs, default=0) + 1

        if day > 25:
            raise ValueError(f'No day was provided as argument to the script. '
                             f'When trying to deduce the day, it got to day {day} which is not valid (maximum is 25). '
                             f'Take a look at the directory and check what is the last day that there is a directory.')

    file_dir = None

    folder_name = 'day-' + f'{day:02d}'

    if output or explicit_save:
        file_dir = os.path.join(output if output else '.', folder_name, 'README.md')

    input_dir = None

    if download_input:
        input_dir = os.path.join(output if output else '.', folder_name, 'input.txt')

    return year, day, file_dir, input_dir


# JavaScript version: https://github.com/kfarnung/aoc-to-markdown
if __name__ == '__main__':
    problem_year, problem_day, file_directory, input_directory = extract_arguments()

    markdown = get_markdown(problem_year, problem_day)

    write(file_directory, markdown)

    if input_directory:
        write(input_directory, get_input(problem_year, problem_day))
