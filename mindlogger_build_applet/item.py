import simplejson
from github import Github, GithubException
import os

class Item(object):
    def __init__(self, username, repo, cname=None):
        self.data = {
            "@context":"https://www.repronim.org/schema-standardization/contexts/generic.jsonld",
            "@type": "https://www.repronim.org/schema-standardization/schemas/Field.jsonld",
            "schema:schemaVersion": "0.0.1",
            "schema:version": "0.0.1",
        }
        self.username = username
        self.repo = repo
        self.cname = cname
    
    def validate(self):
        # TODO: make sure the @id of the item is valid
        # e.g. that it has no spaces or weird characters
        # TODO: make sure all the basic inputs are the right type
        # e.g prefLabel, altLabel, description, and question are all strings
        pass

    def toJSON(self):
        return simplejson.dumps(self.data)

    def postItem(self):
        g = Github(os.environ['GH_TOKEN'])
        repo = g.get_repo("{user}/{repo}".format(user=self.username, repo=self.repo))
        fid = self.data['@id']
        try:
            repo.create_file("/items/{}.jsonld".format(fid), 
                            "updated {}".format(fid), self.toJSON(),
                            branch="master")
        except GithubException:
            filen = repo.get_file_contents("/items/{}.jsonld".format(fid))
            repo.update_file("/items/{}.jsonld".format(fid), 
                            "updated {}".format(fid), self.toJSON(),
                            filen.sha)

        if not self.cname:  
            url = "https://{user}.github.io/{repo}/items/{fid}.jsonld".format(user=self.username,
                                                                           repo=self.repo,
                                                                           fid=fid)
        else:
            url = "https://{cname}/{repo}/items/{fid}.jsonld".format(cname=self.cname,
                                                             repo=self.repo,
                                                             fid=fid)

        return url

    def importItem(self, url):
        raise NotImplementedError("""This method will eventually import an item by a URL""")

class RadioResponseOptions(object):
    def __init__(self, minValue, maxValue, required, choices, type="xsd:int"):
        self.data = dict(minValue=minValue,
                         maxValue=maxValue,
                         requiredValue=required,
                         )
        self.data['choices'] = [{'schema:name': c['name'], 'schema:value': c['value']} for c in choices]

    def toJSON(self):
        return simplejson.dumps(self.data)

class Radio(Item):
    def __init__(self, username, repo, item_id, cname=None, prefLabel="", altLabel="",
                 description="", question="", responseOptions={}):
        """
        inputs
        ------
        username: github username
        repo: github repo name to post the item to
        item_id: string, the id for your item
        prefLabel: string, the title of your item
        altLabel: string, the shortened title of your item
        description: string, the description of your item
        question: string, the question that is asked
        responseOptions: dict, of the form:
            {
                minValue: number or string, minimum value for this item
                maxValue: number of string, maximum value for this item
                required: bool, whether or not a repsonse is required
                type: string, datatype
                choices: list, list of dictionaries with form:
                    {
                        name: string, label that is displayed,
                        value: number, value that this option represents
                    }
            }
        
        
        """
        super().__init__(username, repo, cname)
        self.data['@id'] = item_id
        self.data["skos:prefLabel"] = prefLabel
        self.data["skos:altLabel"] = altLabel
        self.data["schema:description"] = description
        self.data["question"] = question
        self.data["ui"] = {
            "inputType": "radio"
        }
        self.data["responseOptions"] = RadioResponseOptions(**responseOptions).data
        self.validate()