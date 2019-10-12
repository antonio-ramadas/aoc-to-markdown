import codecs

from setuptools import setup

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read().encode('ascii', 'ignore').decode('ascii')

setup(
    name='aoc-to-markdown',
    version='0.2.3',
    description='Parses Advent Of Code problem statement to markdown with option to also download the input while '
                'keeping everything organised',
    long_description=long_description,
    python_requires=">=3.*",
    install_requires=['beautifulsoup4', 'requests'],
    py_modules=['aoc_to_markdown'],
    entry_points={
        'console_scripts': ['aoc-to-markdown=aoc_to_markdown:main']
    },
    url='https://github.com/antonio-ramadas/aoc-to-markdown',
    license='MIT',
    author='António Ramadas',
    author_email='antonio_ramadas@hotmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
