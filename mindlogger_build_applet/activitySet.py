import simplejson
import os
from github import Github, GithubException
from IPython.display import display, HTML

from .utils import BaseNode


class ActivitySetContext(BaseNode):
    default_init_data = {
        '@context': {
            "@version": 1.1,
        }
    }

    def __init__(self, activity_set, **kwargs):
        self.activity_set = activity_set
        super().__init__(**kwargs)
        self.set_activities()

    def get_path(self):
        return "activitySets/{0}/{0}_context.jsonld".format(
            self.activity_set.node_id)

    def set_activities(self):
        for activity in self.activity_set.activities:
            self.data['@context'][activity.data['@id']] = {
                '@id': activity.get_uri(),
                '@type': '@id',
            }

    def get_data(self):
        self.set_activities()
        return self.data


class ActivitySet(BaseNode):
    default_init_data = {
        "@context":["https://www.repronim.org/schema-standardization/contexts/generic.jsonld"],
        "@type": "https://www.repronim.org/schema-standardization/schemas/ActivitySet.jsonld",
        "schema:schemaVersion": "0.0.1",
        "schema:version": "0.0.1",
    }

    # Map parameter to JSONLD key and default value.
    set_data_mapping = {
        "prefLabel": ("skos:prefLabel", ""),
        "altLabel": ("skos:altLabel", ""),
        "description": ("schema:description", ""),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data['@id'] = self.node_id
        self.activities = []
        self.previewURL_base = "https://schema-ui.anisha.pizza/#/activities/0?url="
        self.mindloggerURL_base = "https://web.mindlogger.org/#/?inviteURL="
        self.context = ActivitySetContext(activity_set=self, **kwargs)
        if self.context.get_uri() not in self.data["@context"]:
            self.data["@context"].append(self.context.get_uri())

    def get_path(self):
        return "activitySets/{0}/{0}_schema.jsonld".format(
            self.node_id)

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
            "activity_display_name": {},
        }
        ui = self.data.get("ui", ui_default)
        if "allow" in kwargs:
            ui["allow"] = kwargs["allow"]
        if "shuffle" in kwargs:
            ui["shuffle"] = kwargs["shuffle"]
        self.data["ui"] = ui

        self.extra_context = {
            '@context': {
                "@version": 1.1,
            }
        }

        self.previewURL = None
        self.mindloggerURL = None

    def addImage(self):
        raise NotImplementedError("""
        TODO: point to an image on the computer and push it to the github repo.
        then take the URL and add it to the "schema:image" property of self.data
        """)
    
    def addAbout(self):
        raise NotImplementedError("""
        TODO: point to a markdown file on the computer and push it to the github repo
        then take the URL and add it to the "schema:about" property of self.data
        """)

    def set_activities(self):
        variableMap_items = [
            vm["variableName"] for vm in
            self.data["variableMap"]
        ]
        for activity in self.activities:
            if activity.data["@id"] not in variableMap_items:
                self.data['variableMap'].append({
                    "variableName": activity.data['@id'],
                    "isAbout": activity.data['@id'],
                })

    def setActivity(self, activity, displayName, visibility=True):
        # TODO: make sure item is of type Activity

        # Add or overwrite item in self.activity.
        new_activities = [a for a in self.activities if a.data["@id"] != activity.data["@id"]]
        new_activities.append(activity)
        self.activities = new_activities
        self.set_activities()

        # Add item to UI.
        self.data['ui']['visibility'][activity.data['@id']] = visibility
        self.data['ui']['activity_display_name'][activity.data['@id']] = displayName
        if activity.data["@id"] not in self.data["ui"]["order"]:
            self.data['ui']['order'].append(activity.data['@id'])

    def preview(self):
        return HTML("""
            <p style="margin-bottom: 2em;">
                Preview your activity set at <a target="_blank" href="{url}">{url}</a>
            </p>
            <p>
                <b>Turn OFF your browser cache if things aren't updating</b>
            </p>
        """.format(url=(self.previewURL_base + self.get_uri())))

    def mindlogger(self):
        return HTML("""
            <p style="margin-bottom: 2em;">
                Invite yourself to your applet on Mindlogger at <a target="_blank" href="{url}">{url}</a>
            </p>
            <p>
                <b>Turn OFF your browser cache if things aren't updating</b>
            </p>
        """.format(url=(self.mindloggerURL_base + self.get_uri())))