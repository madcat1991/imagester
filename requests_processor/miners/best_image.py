# coding: utf-8
from regaindapi import Client
from requests import HTTPError

from requests_processor.exceptions import ApiUnknownException, ApiUnexpectedResponseException
from requests_processor.functions import f1_score


class BestImageMiner(Client):
    def get_imagester_metric(self, img_path):
        try:
            res = self.metrics(img_path, ["aesthetics", "exposure"])
        except HTTPError as e:
            raise ApiUnknownException(u"Unknown HTTP error: %s", e)
        except Exception as e:
            raise ApiUnknownException(u"Unknown exception: %s", e)

        try:
            aesthetics = res["aesthetics"]["aesthetics"]
            exposure = res["exposure"]
        except (KeyError, TypeError):
            raise ApiUnexpectedResponseException(u"Unexpected response: %s", img_path, res)

        return f1_score(aesthetics, exposure)
