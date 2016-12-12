# coding: utf-8
import csv
import glob
import os
import urllib
from datetime import datetime


class EngTimeMiner(object):
    def __init__(self, data_url, data_dir):
        self.eng_v = self.get_eng_v(data_url, data_dir)

    def _get_pos(self, day, hour):
        return day * 24 + hour

    def _get_day_and_hour(self, pos):
        return pos / 24, pos % 24

    def get_eng_v(self, data_url, dir_path):
        today = datetime.today()

        data_files = glob.glob(os.path.join(dir_path, "engagement_*.csv"))
        if len(data_files) == 0:
            data_path = os.path.join(os.path.join(dir_path, today.strftime('engagement_%Y%m%d.csv')))
            urllib.urlretrieve(data_url, data_path)
        else:
            data_path = data_files[0]
            download_day = datetime.strptime(os.path.basename(data_path), 'engagement_%Y%m%d.csv')
            if (today - download_day).days >= 7:
                data_path = os.path.join(os.path.join(dir_path, today.strftime('engagement_%Y%m%d.csv')))
                urllib.urlretrieve(data_url, data_path)

        eng_v = [0] * (7 * 24)
        with open(data_path, 'rU') as f:
            reader = csv.reader(f)

            # skipping first two rows
            reader.next()
            reader.next()

            for hour, row in enumerate(reader):
                for i in range(1, 8):
                    weekday = (i + 5) % 7
                    pos = self._get_pos(weekday, hour)
                    eng_v[pos] = float(row[i].replace("%", ''))
        return eng_v

    def get_eng_time(self):
        dt = datetime.now()
        first_pos = self._get_pos(dt.weekday(), dt.hour)
        last_pos = (first_pos + 24) % len(self.eng_v)

        if first_pos < last_pos:
            interval = self.eng_v[first_pos: last_pos]
        else:
            interval = self.eng_v[first_pos:] + self.eng_v[:last_pos]

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

        closest_pos = (first_pos + closest) % len(self.eng_v)
        best_pos = (first_pos + best) % len(self.eng_v)

        return self._get_day_and_hour(closest_pos), self._get_day_and_hour(best_pos)
