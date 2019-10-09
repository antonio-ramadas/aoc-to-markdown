import os
import re
import sys
from datetime import datetime
from distutils.errors import DistutilsFileError
from distutils.file_util import copy_file
from getopt import getopt, GetoptError
from distutils.dir_util import copy_tree

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


def copy(src, dst):
    try:
        copy_tree(src, dst)
    except DistutilsFileError:
        copy_file(src, dst)


def print_usage():
    print(f'Usage: {sys.argv[0]} [-h] [-y <year>] [-d <day>] [-o <output_dir>] [-b <boilerplate>] [-s] [-i]')
    print(' -h, --help          Optional parameter to print this message')
    print(' -y, --year          Optional parameter to indicate the year of the problem')
    print(' -d, --day           Optional parameter to indicate the day of the problem')
    print(' -o, --output        Optional parameter to indicate the path of the output (default = ".")')
    print(' -b, --boilerplate   Optional parameter to copy a directory/file to the output')
    print(' -s, --save          Optional argument to indicate that the markdown should not be printed to stdout, but to'
          ' a file')
    print(' -i, --input         Optional argument to indicate that the input is to be downloaded and saved to a file')
    print()
    print('Extended description:')
    print('--year, if not given, defaults to the current year if in december; otherwise is the current year')
    print('--day, if not given, defaults to the first day which has not been retrieved (checks for directories named '
          '"day-<day>"); if all days have been retrieved, then go drink some hot chocolate and enjoy the rest of the '
          'day')
    print('--output is the prefix path where the folder (syntax: "day-<day>") will be created')
    print('--boilerplate is an argument useful to copy the solution boilerplate to help you get started')
    print('--save is only necessary if you want to save directly to a file and --output is not given')
    print()
    print('Example:')
    print(f'{sys.argv[0]} -y 2018 -d 1 -o my-solution-directory -b my-boilerplate -i')


def parse_arguments():
    try:
        opts, args = getopt(sys.argv[1:], 'y:d:o:b:si', ['year=', 'day=', 'output=', 'boilerplate=', 'save', 'input'])
    except GetoptError:
        print_usage()
        sys.exit(1)

    year = None
    day = None
    output = None
    boilerplate_from_arg = None
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
        elif opt in ('-b', '--boilerplate'):
            boilerplate_from_arg = arg
        elif opt in ('-s', '--save'):
            explicit_save = True
        elif opt in ('-i', '--input'):
            download_input = True

    return year, day, output, boilerplate_from_arg, explicit_save, download_input


def extract_arguments():
    year, day, output, boilerplate_from_arg, explicit_save, download_input = parse_arguments()

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

    folder_name = 'day-' + f'{day:02d}'

    file_dir = None
    if output or explicit_save:
        file_dir = os.path.join(output if output else '.', folder_name, 'README.md')

    input_dir = None
    if download_input:
        input_dir = os.path.join(output if output else '.', folder_name, 'input.txt')

    boilerplate_to_dir = os.path.join(output if output else '.', folder_name)

    return year, day, file_dir, input_dir, boilerplate_from_arg, boilerplate_to_dir


# JavaScript version: https://github.com/kfarnung/aoc-to-markdown
if __name__ == '__main__':
    problem_year, problem_day, file_directory, input_directory, boilerplate_from, boilerplate_to = \
        extract_arguments()

    markdown = get_markdown(problem_year, problem_day)

    write(file_directory, markdown)

    if input_directory:
        write(input_directory, get_input(problem_year, problem_day))

    if boilerplate_from and boilerplate_to:
        copy(boilerplate_from, boilerplate_to)
