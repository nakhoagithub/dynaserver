from dyna.document import Document, StringField, ReferenceField, DateTimeField, ListField, BooleanField, ObjectIdField


class ExamplePermission(Document):
    name = StringField()
    id_collection = ReferenceField("Collection")
    access = BooleanField()

    meta = {
        "collection": "example_permission"
    }


class ExampleRole(Document):
    name = StringField()
    ids_permission = ListField(ReferenceField(ExamplePermission))
    ids_permission_test = ListField(ReferenceField(ExamplePermission))

    meta = {
        "collection": "example_role"
    }


class ExampleAccount(Document):
    name = StringField()
    ids_role = ListField(ReferenceField(ExampleRole))
    date = DateTimeField()
    object_id = ObjectIdField()

    meta = {
        "collection": "example_account"
    }