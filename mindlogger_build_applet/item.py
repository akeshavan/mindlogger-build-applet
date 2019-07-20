import simplejson
from github import Github, GithubException
import os

from .utils import BaseNode


class Item(BaseNode):
    default_init_data = {
        "@context":"https://www.repronim.org/schema-standardization/contexts/generic.jsonld",
        "@type": "https://www.repronim.org/schema-standardization/schemas/Field.jsonld",
        "schema:schemaVersion": "0.0.1",
        "schema:version": "0.0.1",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data['@id'] = self.node_id

    def validate(self):
        # TODO: make sure the @id of the item is valid
        # e.g. that it has no spaces or weird characters
        # TODO: make sure all the basic inputs are the right type
        # e.g prefLabel, altLabel, description, and question are all strings
        pass

    def get_path(self):
        return "items/{}.jsonld".format(self.node_id)


class RadioResponseOptions(object):
    def __init__(self, minValue, maxValue, required, choices, type="xsd:int"):
        self.data = dict(minValue=minValue,
                         maxValue=maxValue,
                         requiredValue=required,
                         )
        self.data["choices"] = [{"schema:name": c["name"], "schema:value": c["value"]} for c in choices]

        # TODO: if c["image"] exits, add "schema:image" in the list above.


class Radio(Item):
    set_data_mapping = {
        "prefLabel": ("skos:prefLabel", ""),
        "altLabel": ("skos:altLabel", ""),
        "description": ("schema:description", ""),
        "question": ("question", ""),
    }

    def set_data(self, **kwargs):
        """
        Use to set prefLabel, altLabel, description, question, responseOptions.

        Overrides parent class to provide support for setting responseOptions.
        """
        super().set_data(**kwargs)
        if "responseOptions" in kwargs:
            self.data["responseOptions"] = RadioResponseOptions(**kwargs["responseOptions"]).data
        elif "responseOptions" not in self.data:
            self.data["responseOptions"] = {}
        

    def get_default_data(self):
        """
        Add Radio-specific data to initialization.
        """
        default_init_data = super().get_default_data()
        default_init_data["ui"] = {
            "inputType": "radio",
            "allow": ["autoAdvance"],
        }
        return default_init_data