import simplejson
import os

from .utils import BaseNode


class ActivityContext(BaseNode):
    default_init_data = {
        '@context': {
            "@version": 1.1,
        }
    }

    def __init__(self, activity, **kwargs):
        self.activity = activity
        super().__init__(**kwargs)
        self.set_items()

    def get_path(self):
        return "activities/{}_context.jsonld".format(self.activity.node_id)

    def set_items(self):
        for item in self.activity.items:
            self.data["@context"][item.data['@id']] = {
                '@id': item.get_uri(),
                '@type': '@id',
            }

    def get_data(self):
        self.set_items()
        return self.data


class Activity(BaseNode):
    default_init_data = {
        "@context":["https://www.repronim.org/schema-standardization/contexts/generic.jsonld"],
        "@type": "https://www.repronim.org/schema-standardization/schemas/Activity.jsonld",
        "schema:schemaVersion": "0.0.1",
        "schema:version": "0.0.1",
    }

    # Map parameter to JSONLD key and default value.
    set_data_mapping = {
        "prefLabel": ("skos:prefLabel", ""),
        "altLabel": ("skos:altLabel", ""),
        "description": ("schema:description", ""),
        "preamble": ("preamble", ""),
    }

    def  __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data['@id'] = self.node_id
        self.items = []
        self.context = ActivityContext(activity=self, **kwargs)
        if self.context.get_uri() not in self.data["@context"]:
            self.data["@context"].append(self.context.get_uri())

    def get_path(self):
        return "activities/{}_schema.jsonld".format(self.node_id)

    def set_data(self, **kwargs):
        super().set_data(**kwargs)

        if "variableMap" not in self.data:
            self.data["variableMap"] = []

        # UI adds defaults unless existing or provided.
        ui_default = {
            "allow": ["skipped", "dontKnow"],
            "shuffle": False,
            "order": [],
            "visibility": {},
        }
        ui = self.data.get("ui", ui_default)
        if "allow" in kwargs:
            ui["allow"] = kwargs["allow"]
        if "shuffle" in kwargs:
            ui["shuffle"] = kwargs["shuffle"]
        self.data["ui"] = ui

    def set_items(self):
        variableMap_items = [
            vm["variableName"] for vm in
            self.data["variableMap"]
        ]
        for item in self.items:
            if item.data["@id"] not in variableMap_items:
                self.data['variableMap'].append({
                    "variableName": item.data['@id'],
                    "isAbout": item.data['@id'],
                })

    def setItem(self, item, visibility=True):
        # TODO: make sure item is of type Item

        # Add or overwrite item in self.items.
        new_items = [i for i in self.items if i.data["@id"] != item.data["@id"]]
        new_items.append(item)
        self.items = new_items
        self.set_items()

        # Add item to UI.
        self.data['ui']['visibility'][item.data['@id']] = visibility        
        if item.data["@id"] not in self.data["ui"]["order"]:
            self.data['ui']['order'].append(item.data['@id'])