from typing import List
from mongoengine import Document
from mongoengine.queryset.queryset import QuerySet


class BaseDocument(Document):
    
    meta = {
        "abstract": True
    }

    def query(self, *args, **kwargs) -> QuerySet:
        raise NotImplementedError
    
    def count(self, **kwargs) -> int:
        raise NotImplementedError
    
    def convert_filter(self, filter_values: dict, **kwargs):
        raise NotImplementedError
    
    def get(self, filter_values: dict = {}, first: bool = False, limit: int = None, skip: int = None, sort: dict = None, **kwargs) -> List["BaseDocument"] | "BaseDocument" | None:
        raise NotImplementedError
    
    def create(self, values: dict, **kwargs):
        raise NotImplementedError
    
    def update(self, values: dict, upsert=False, **kwargs):
        raise NotImplementedError
    
    def update_where(self, filter_values: dict, values: dict, **kwargs) -> List:
        raise NotImplementedError
    
    def delete(self, id: str, **kwargs):
        raise NotImplementedError

    def delete_where(self, filter_values: dict, **kwargs):
        raise NotImplementedError
    
    def json(self, ignore_field: List[str] = None, **kwargs):
        raise NotImplementedError