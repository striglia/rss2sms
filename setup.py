from setuptools import setup, find_packages
import codecs
import os
import re


def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the relevant file
with codecs.open('DESCRIPTION.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="rss2sms",
    version=find_version('rss2sms', '__init__.py'),
    description="An sms alerter for updates to an rss feed",
    long_description=long_description,
    url='http://github.com/striglia/rss2sms',
    author='Scott Triglia',
    author_email='scott.triglia@gmail.com',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='rss sms alerts',

    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'feedparser',
        'tinyurl',
        'twilio',
    ],
    entry_points={
        'console_scripts': [
            'rss2sms=rss2sms:main',
        ],
    },
)
