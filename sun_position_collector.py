import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import csv


# Arguments
DATE = None
HOURS = [13, 14]  # 0 ~ 23 integer
MINUTES = [0, 30]  # 0 ~ 59 integer
SECONDS = [0]  # 0 ~ 59 integer
LAT = 37.54980  # latitude
LONG = 126.9671  # longitude
ELEVATION = 0
###


class Collector:

    def __init__(self):
        self.url = ''
        self.azimuth = 0.0
        self.altitude = 0.0
        self.ascension = 0.0
        self.declination = 0.0


    def set_url(self, date, hour, minute, second, lat, lon, elv):
        self.url = 'https://astro.kasi.re.kr/'
        self.url += 'life/pageView/10?useElevation=1'
        self.url += '&lat={}&lng={}&elevation={}'.format(lat, lon, elv)
        self.url += '&output_range=2'
        self.url += '&date={}'.format(date)
        self.url += '&hour={}&minute={}&second={}'.format(hour, minute, second)


    def scrape(self):
        driver = webdriver.Firefox()
        driver.get(self.url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        nodes = soup.find(id='sun-height-table').find('tbody').select('td')
        azi = list(map(float, nodes[0].text.split(' ')))  # [degree, minute, second]
        alt = list(map(float, nodes[1].text.split(' ')))
        asc = list(map(float, nodes[2].text.split(' ')))
        dec = list(map(float, nodes[3].text.split(' ')))
        self.azimuth = azi[0] + azi[1] / 60 + azi[2] / 3600
        self.altitude = alt[0] + alt[1] / 60 + alt[2] / 3600
        self.ascension = asc[0] + asc[1] / 60 + asc[2] / 3600
        self.declination = dec[0] + dec[1] / 60 + dec[2] / 3600
        driver.close()


def main():
    if len(sys.argv) > 1:
        if DATE is not None:
            print('Warning: Command line argument have priority over the value of `DATE` specified in the script.')
        DATE = sys.argv[1]
    elif DATE is None:
        print('Error: argument `DATE` is empty.')
        return

    (year, month, day) = map(int, DATE.split('-'))

    with open('sun_position.csv', 'w') as outfile:
        csv_w = csv.writer(outfile)
        csv_w.writerow(['year', 'month', 'day', 'hour', 'minute', 'second',
                        'azimute', 'altitude', 'right_ascension', 'declination'])

        clt = Collector()

        for h in HOURS:
            for m in MINUTES:
                for s in SECONDS:
                    clt.set_url(DATE, h, m, s, LAT, LONG, ELEVATION)
                    clt.scrape()
                    csv_w.writerow([year, month, day, h, m, s,
                                    clt.azimuth, clt.altitude, clt.ascension, clt.declination])

                    process_info = '{} {}:{}:{}'.format(DATE, h, m, s)
                    process_info += ' ({:.1f}, {:.1f}, {:.1f}, {:.1f})'.format(
                        clt.azimuth, clt.altitude, clt.ascension, clt.declination
                    )
                    print(process_info)


main()
