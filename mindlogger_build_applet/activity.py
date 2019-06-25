import simplejson
import os
from github import Github, GithubException

class Activity():
    def __init__(self, user, repo, activity_id, cname=None, prefLabel="", altLabel="",
                 description="", preamble="", scoringLogic={},
                 allow=['skipped', 'dontKnow'], shuffle=False):
        
        self.user = user
        self.repo = repo
        self.cname = cname
        g = Github(os.environ['GH_TOKEN'])
        gh_repo = g.get_repo("{user}/{repo}".format(user=self.user, repo=self.repo))
        
        self.gh_repo = gh_repo

        self.data = {
                "@context":["https://www.repronim.org/schema-standardization/contexts/generic.jsonld"],
                "@type": "https://www.repronim.org/schema-standardization/schemas/Activity.jsonld",
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
        # TODO: make sure item is of type Item
        item_url = item.postItem()

        # TODO: make sure the item isn't already in the variableMap
        self.data['variableMap'].append({
            "variableName": item.data['@id'],
            "isAbout": item.data['@id'],
        })
        self.data['ui']['visibility'][item.data['@id']] = visibility
        
        # TODO: make sure the item isn't already in the context
        self.extra_context['@context'][item.data['@id']] = {
            '@id': item_url,
            '@type': '@id',
        }

        # TODO: make sure the item isn't already in the list
        self.data['ui']['order'].append(item.data['@id'])

    
    def postActivityContext(self):
        """
        
        """
        fid = self.data['@id']
        try:
            self.gh_repo.create_file("/activities/{}_context.jsonld".format(fid), 
                            "updated {}_context".format(fid),
                            simplejson.dumps(self.extra_context),
                            branch="master")
        except GithubException:
            filen = self.gh_repo.get_file_contents("/activities/{}_context.jsonld".format(fid))
            self.gh_repo.update_file("/activities/{}_context.jsonld".format(fid), 
                            "updated {}_context".format(fid), self.toJSON(),
                            filen.sha)
        if not self.cname:
            url = "https://{user}.github.io/{repo}/activities/{fid}_context.jsonld".format(user=self.user,
                                                                           repo=self.repo,
                                                                           fid=fid)
        else:
            url = "https://{cname}/{repo}/activities/{fid}_context.jsonld".format(
                                                                cname=self.cname,
                                                                repo=self.repo,
                                                                fid=fid)

        return url


    def postActivity(self):
        # 1. post the extra context
        context_url = self.postActivityContext()


        # 2. update self.data.context with URL
        self.data['@context'].append(context_url)

        # 3. post self.data into the activities folder
        fid = self.data['@id']
        try:
            self.gh_repo.create_file("/activities/{}_schema.jsonld".format(fid), 
                            "updated {}".format(fid), self.toJSON(),
                            branch="master")
        except GithubException:
            filen = self.gh_repo.get_file_contents("/activities/{}_schema.jsonld".format(fid))
            self.gh_repo.update_file("/activities/{}_schema.jsonld".format(fid), 
                            "updated {}".format(fid), self.toJSON(),
                            filen.sha)
        
        if not self.cname:
            url = "https://{user}.github.io/{repo}/activities/{fid}_schema.jsonld".format(user=self.user,
                                                                           repo=self.repo,
                                                                           fid=fid)
        else:
            url = "https://{cname}/{repo}/activities/{fid}_schema.jsonld".format(cname=self.cname,
                                                                repo=self.repo,
                                                                fid=fid)
        return url
        