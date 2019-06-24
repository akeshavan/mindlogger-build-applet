import simplejson

class Activity():
    def __init__(self, activity_id, prefLabel="", altLabel="",
                 description="", preamble="", scoringLogic={},
                 allow=['skipped', 'dontKnow'], shuffle=False):
        self.data = {
                "@context":["http://www.repronim.org/schema-standardization/contexts/generic.jsonld"],
                "@type": "http://www.repronim.org/schema-standardization/schemas/Activity.jsonld",
                "schema:schemaVersion": "0.0.1",
                "schema:version": "0.0.1",
            }
        self.data['@id'] = activity_id
        self.data["skos:prefLabel"] = prefLabel
        self.data["skos:altLabel"] = altLabel
        self.data["schema:description"] = description
        self.data["preamble"] = preamble
        self.data['variableMap'] = []
        self.data["ui"] = dict(shuffle=shuffle, allow=allow, order=[], visibility={})

        self.extra_context = {
            '@context': {
                "@version": 1.1,
            }
        }
    
    def toJSON(self):
        return simplejson.dumps(self.data)

    def addItem(self, item, visibility=True):
        item_url = item.postItem()
        self.data['variableMap'].append({
            "variableName": item.data['@id'],
            "isAbout": item.data['@id'],
        })
        self.data['ui']['visibility'] = visibility
        self.extra_context[item.data['@id']] = {
            '@id': item_url,
            '@type': '@id',
        }
        self.data['ui']['order'].append(item.data['@id'])

    def postActivityContext(self):
        raise NotImplementedError("""
        Eventually, this method will post the context file
        """)    
    
    def postActivity(self):
        # 1. post the extra context
        # 2. update self.data.context with URL
        # 3. post self.data
        raise NotImplementedError("""
            eventually, this method will post the activity to github
        """)
        