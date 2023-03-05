import datetime

from typing import Dict


class APIException(Exception):
    __slots__ = [
        'type',
        'title',
        'status',
        'detail',
        'instance',
        'timestamp',
    ]

    def __init__(
            self,
            type_: str,
            title_: str,
            status_: int,
            detail_: str,
            instance_: str,
            timestamp_: datetime.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ):
        self.type = type_
        self.title = title_
        self.status = status_
        self.detail = detail_
        self.instance = instance_
        self.timestamp = timestamp_

    @property
    def content(self) -> Dict[str, Dict[str, str | int]]:
        exc = {
            'type': self.type,
            'title': self.title,
            'status': self.status,
            'detail': self.detail,
            'instance': self.instance,
            'timestamp': str(self.timestamp)
        }

        error = {
            'error': exc
        }

        return error

    @property
    def headers(self) -> Dict[str, str]:
        h = {
            'API-Error': 'Exception: {}'.format(self.type),
            'content-type': 'application/json'
        }
        return h
