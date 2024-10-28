import json
from typing import List, Literal, Any
from datetime import datetime, timezone
from bson import ObjectId
from mongoengine import EmbeddedDocument
from mongoengine.fields import *
from mongoengine.queryset.queryset import QuerySet

from dyna.socketio.socket import socketio
from dyna.tools.dict import convert_date
from dyna.tools.dict import rename, delete_keys, convert_key
from dyna.environment import env
from dyna.base.document import BaseDocument

def get_document_class(collection_name: str):
    """
    Get class "Document" from env with `collection_name`
    """
    doc = env.get(collection_name, None)
    if doc is not None:
        return doc.__class__

# def method_rpc(func):
#     def wrapper(self, *args, **kwargs):
#         result = func(self, *args, **kwargs)
#         return result
#     return wrapper

class Document(BaseDocument):
    _description = None
    _id_collection = ""
    _collection_name = ""
    meta = {
        "allow_inheritance": False,
        "abstract": True,
        "indexes": [
            "created_at",
        ],
        "id_field": "id",
        "strict": False,
    }

    def __init__(self, *args, **values):
        self.env = env
        if self._description == None:
            self._description = f"Document: {self.__class__.__name__}"
        super().__init__(*args, **values)

    id = StringField(primary_key=True)
    created_at = DateTimeField()
    modified_at = DateTimeField()

    allow_method_crud: Literal["create", "read", "update", "delete"] = ["create", "read", "update", "delete"]
    allow_method_rpc: List[str] = []
    ignore_field_read = []
    ignore_field_create = []
    ignore_field_update = []
    socket_ref = {}
    enable_socket = False

    def __init_subclass__(self) -> None:
        env[self.__name__] = self()
        self._collection_name = self.__name__
        metadata: dict = self._meta
        id_collection = metadata.get("collection", None)
        if id_collection is not None:
            self._id_collection = id_collection

        return super().__init_subclass__()

    @classmethod
    def query(self, *args, **kwargs) -> QuerySet:
        return self.objects(*args, **kwargs)
    
    def count(self, filter_values: dict = None) -> int:
        if filter_values:
            return self.query(__raw__=filter_values).count()
        return self.query().count()

    def convert_filter(self, filter_values: dict):
        new_filters = convert_date(filter_values)
        return new_filters
    
    def populate(self, document: "Document", ref: dict = {}):
        values = document.json()
        try:
            if len(ref.keys()) > 0:
                for field_name, field in document._fields.items():
                    if isinstance(field, ReferenceField):
                        ref_doc = getattr(document, field_name)
                        if ref_doc is not None and field_name in ref.keys():
                            new_ref = {}
                            if isinstance(ref[field_name], dict):
                                new_ref = ref[field_name]
                            new_values = self.populate(ref_doc, ref=new_ref)
                            values[f"$ref.{field_name}"] = new_values
                    elif isinstance(field, ListField) and isinstance(field.field, ReferenceField):
                        ref_docs = getattr(document, field_name)
                        if field_name in ref.keys():
                            new_values_list = []
                            for i in range(len(ref_docs)):
                                new_ref = {}
                                if isinstance(ref[field_name], dict):
                                    new_ref = ref[field_name]
                                new_values = self.populate(ref_docs[i], ref=new_ref)
                                new_values_list.append(new_values)
                            values[f"$ref.{field_name}"] = new_values_list
        except Exception as e:
            pass
        return values

    def get(
        self, 
        filter_values: dict,
        first: bool = False,
        limit: int = None,
        skip: int = None,
        sort: dict = None,
        **kwargs,
    )  -> List["Document"] | "Document" | None:
        if not filter_values:
            filter_values = {}

        filter_values = rename(filter_values, "id", "_id")
        filter_values = self.convert_filter(filter_values)
        result = self.query(__raw__=filter_values)
        if sort is not None:
            sort_value = [k if v != -1 else f"-{k}" for k, v in sort.items()]
            result = result.order_by(*sort_value)
        if limit is not None:
            result = result.limit(limit)
        if skip is not None:
            result = result.skip(skip)

        distinct = kwargs.get("distinct")
        if distinct:
            result = result.distinct(distinct)
            
        if first:
            result = result.first()

        if kwargs.get("total_with_filter", False):
            count = 0

            # count là số lương của distinct
            if distinct:
                count = len(result)
            else:
                count = self.query(__raw__=filter_values).count()
            return result, count

        return result

    def create(
        self,
        values: dict,
        **kwargs,
    ):
        id_: str = values.get("id", str(ObjectId()))
        values["id"] = id_
        values["created_at"] = {"$date": datetime.now(timezone.utc).timestamp() * 1000}
        values["modified_at"] = {"$date": datetime.now(timezone.utc).timestamp() * 1000}
        values = delete_keys(values, [i for i in self.ignore_field_create])
        doc = self.from_json(json.dumps(values))
        doc.save(force_insert=True)

        # Socket IO
        disable_socket = kwargs.get("disable_socket", False)
        if not disable_socket:
            self.send_socket(doc, type_socket="create", **kwargs)
        return doc
    
    def update(
        self,
        values: dict,
        upsert=False,
        **kwargs,
    ):
        values["modified_at"] = {"$date": datetime.now(timezone.utc).timestamp() * 1000}
        values = delete_keys(values, [i for i in self.ignore_field_update])

        if values.get("id", None) is None:
            raise ValueError("\"id\" field is required")
        id_ = values.get("id")

        data = None
        if kwargs.get("document", None):
            data = kwargs.get("document")
        else:
            data = self.get({"id": id_}, first=True)
        
        if data is not None:
            _doc = {k: v for k, v in data.to_mongo().items() if k not in ["id", "_id"]}
            _values = {k: v for k, v in self.from_json(json.dumps(values)).to_mongo().items() if k not in ["id", "_id"] and k in values}
            values_update = {**_doc, **_values, **{k: v for k, v in values.items() if v is  None}}
            obj = data.__class__(id=data.id, **values_update)
            doc = obj.save()
            
            # Socket IO
            disable_socket = kwargs.get("disable_socket", False)
            if not disable_socket:
                self.send_socket(doc, type_socket="update", **kwargs)
            return doc

        elif upsert:
            return self.create(values, **kwargs)

    def update_where(
        self,
        filter_values: dict,
        values: dict,
        **kwargs,
    ) -> List:
        values["modified_at"] = {"$date": datetime.now(timezone.utc).timestamp() * 1000}
        values = delete_keys(values, [i for i in self.ignore_field_update])
        documents = self.get(filter_values=filter_values)
        results = []
        for document in documents:
            _values = {k: v for k, v in values.items() if k not in ["id", "_id"]}
            result = self.update({"id": document.id, **_values}, document=document, **kwargs)
            results.append(result)
        return results
    
    def delete(
        self,
        id: str,
        **kwargs,
    ):
        doc = kwargs.get("obj", None)
        if not doc:
            doc = self.get({"id": id}, first=True)
        self.query(__raw__={"_id": id}).delete()
        
        # Socket IO
        disable_socket = kwargs.get("disable_socket", False)
        if not disable_socket:
            self.send_socket(doc, "delete", **kwargs)
        return id
    
    def delete_where(
        self,
        filter_values: dict,
        **kwargs
    ):
        documents = self.get(filter_values=filter_values)
        deleted = []
        for i in documents:
            i.delete(i.id, doc=i, **kwargs)
            deleted.append(i.id)
        return deleted
    
    def push_item(self, filter_values: dict, field_name: str, item: Any, **kwargs):
        filter_values = rename(filter_values, "id", "_id")
        filter_values = self.convert_filter(filter_values)
        r = self.query(__raw__=filter_values).update(__raw__={"$push": {field_name: item}})
        if r:
            docs = self.get(filter_values=filter_values)
            for doc in docs:
                self.send_socket(doc, "update", **kwargs)

    def remove_item(self, filter_values: dict, field_name: str, item: Any, **kwargs):
        filter_values = rename(filter_values, "id", "_id")
        filter_values = self.convert_filter(filter_values)
        r = self.query(__raw__=filter_values).update(__raw__={"$pull": {field_name: item}})
        if r:
            docs = self.get(filter_values=filter_values)
            for doc in docs:
                self.send_socket(doc, "update", **kwargs)

    def json(self, ignore_field: List[str] = None):
        result = json.loads(self.to_json())
        r = rename(result, "_id", "id")
        r = delete_keys(r, ignore_field or self.ignore_field_read + ["_cls"])
        return r

    def send_socket(self, doc: "Document", type_socket: str, **kwargs):
        socket_to = kwargs.get("socket_to", None)
        if (self.enable_socket or socket_to) and socketio:
            if type(socket_to) is list:
                for i in socket_to:
                    if not i: continue
                    socketio.emit(
                        f"on_{self._collection_name}",
                        {
                            "type": type_socket,
                            "data": self.populate(doc, ref=self.socket_ref)
                        },
                        to=i,
                    )
            elif type(socket_to) is str:
                socketio.emit(
                    f"on_{self._collection_name}",
                    {
                        "type": type_socket,
                        "data": self.populate(doc, ref=self.socket_ref)
                    },
                    to=socket_to,
                )

class DynaEmbeddedDocument(EmbeddedDocument):

    meta = {
        "abstract": True,
        "allow_inheritance": True,
    }

    def json(self):
        result = json.loads(self.to_json())
        r = delete_keys(result, ["_cls"])
        return r