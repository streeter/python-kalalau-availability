#!/usr/bin/env python

import datetime
import sys
from optparse import OptionParser

import requests
from bs4 import BeautifulSoup

RESERVATIONS_URL = (
    'https://camping.ehawaii.gov/camping/all,sites,0,25,1,1692'
    ',,,,{date},5,,1,1427978067756.html')


def find_availability(date):
    date_format = date.strftime('%Y%m%d')
    url = RESERVATIONS_URL.format(date=date_format)

    r = requests.get(url)
    r.raise_for_status()

    data = r.text

    soup = BeautifulSoup(data)

    table = soup.find(id='sites_table')
    if not table:
        raise Exception('Could not find the sites table')

    body = table.find('tbody')
    if not body:
        raise Exception('Could not find the body')

    # Kalalau is the first tr in the body
    kalalau = body.find_all('tr')[0]

    kalalau_tds = kalalau.find_all('td')

    assert kalalau_tds[0].text == u'Kalalau'

    first_night_count = int(kalalau_tds[6].text)

    return first_night_count

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option(
        "-v", "--verbose", dest="verbose", action="store_true",
        default=False, help="Be verbose.")

    today = datetime.date.today()
    optparser.add_option(
        "-y", "--year", dest="year", default=today.year, type="int",
        help="The year to check.")
    optparser.add_option(
        "-m", "--month", dest="month", default=today.month, type="int",
        help="The month to check.")
    optparser.add_option(
        "-d", "--day", dest="day", default=today.day, type="int",
        help="The day to check.")
    optparser.add_option(
        "-n", "--range", dest="range", default=1, type="int",
        help="The range of days after to also check.")

    (options, args) = optparser.parse_args()

    for offset in range(0, options.range):
        date = datetime.datetime(
            options.year, options.month, options.day + offset)

        if options.verbose:
            print('Checking availability on {}...'.format(date.strftime('%x')))

        try:
            count = find_availability(date)
        except Exception as e:
            if options.verbose:
                raise
            sys.exit(e)

        if count > 0:
            if options.verbose:
                print("We have availability! {}".format(count))
            sys.exit(0)

    # Didn't find any availability
    if options.verbose:
        print("No availability for {}".format(date.strftime('%x')))
    sys.exit(1)
