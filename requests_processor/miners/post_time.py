# coding: utf-8
import csv
import glob
import os
import urllib
from datetime import datetime, timedelta

import logging


class PostTimeMiner(object):
    def __init__(self, url, data_dir):
        self.data_dir = data_dir
        self.file_name = "engagement_*.csv"
        self.engagement_per_hour = self._get_engagement_vector(url)

    def _get_pos(self, day, hour):
        return day * 24 + hour

    def _download_data(self, url, name):
        os.makedirs(self.data_dir)
        try:
            data_path = os.path.join(self.data_dir, name)
            urllib.urlretrieve(url, data_path)
        except IOError as e:
            logging.exception(u"Unknown exception: %s", e)
            return None
        return data_path

    def _get_engagement_vector(self, url):
        today = datetime.today()

        data_files = glob.glob(os.path.join(self.data_dir, self.file_name))
        if len(data_files) == 0:
            data_path = self._download_data(url, today.strftime('engagement_%Y%m%d.csv'))
        else:
            data_path = data_files[0]
            download_day = datetime.strptime(os.path.basename(data_path), 'engagement_%Y%m%d.csv')
            if (today - download_day).days >= 7:
                # remove old
                os.unlink(data_path)
                # download new
                data_path = self._download_data(url, today.strftime('engagement_%Y%m%d.csv'))

        engagement_vector = [0] * (7 * 24)
        if data_path is not None:
            with open(data_path, 'rU') as f:
                reader = csv.reader(f)

                # skipping first two rows
                reader.next()
                reader.next()

                for hour, row in enumerate(reader):
                    for i in range(1, 8):
                        weekday = (i + 5) % 7
                        pos = self._get_pos(weekday, hour)
                        engagement_vector[pos] = float(row[i].replace("%", ''))
        return engagement_vector

    def get_best_times(self):
        dt = datetime.now()
        first_pos = self._get_pos(dt.weekday(), dt.hour)
        last_pos = (first_pos + 24) % len(self.engagement_per_hour)

        if first_pos < last_pos:
            interval = self.engagement_per_hour[first_pos: last_pos]
        else:
            interval = self.engagement_per_hour[first_pos:] + self.engagement_per_hour[:last_pos]

        diffs = [interval[i] - interval[i - 1] for i in range(1, len(interval))]

        closest = None
        last = best = None
        delta = best_delta = 0
        for i, d in enumerate(diffs):
            if d >= 0:
                if closest is None:
                    closest = i
                if last is None:
                    last = i
                delta += d
            else:
                if best_delta < delta:
                    # update best
                    best, best_delta = last, delta
                # reset work
                delta, last = 0, None

        if best_delta < delta:
            # update best
            best, best_delta = last, delta

        current_hour = datetime(dt.year, dt.month, dt.day, dt.hour)
        time_closest = current_hour + timedelta(hours=closest)
        time_in_24h = current_hour + timedelta(hours=best)
        return time_closest, time_in_24h
