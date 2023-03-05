import datetime

from typing import List, Union
from pydantic import BaseModel

from data import settings


# Post item model
class PostModel(BaseModel):
    id: int
    text: str
    created_date: datetime.datetime
    rubrics: list

    class Config:
        orm_mode = True


# Dump models
class ResultsModel(BaseModel):
    result: List[PostModel] | str

    class Config:
        orm_mode = True


class DumpModel(BaseModel):
    data: ResultsModel
    meta: dict | str | None = settings.META

    class Config:
        orm_mode = True


# class for dumping any obj
class DumpObj:
    def __init__(self, **atr):
        for key, val in atr.items():
            self.__setattr__(key, val)

    def __getitem__(self, item: str) -> Union[int, str]:
        return getattr(self, item)

    def __repr__(self):
        return "{name_cls}({args})".format(
            name_cls=self.__class__.__name__,
            args=', '.join(
                [
                    "{k}={v}".format(
                        k=k, v=v if type(v) is not str else f"'{v}'"
                    )
                    for k, v in self.__dict__.items()
                ]
            )
        )

    def __str__(self):
        return self.__repr__()
