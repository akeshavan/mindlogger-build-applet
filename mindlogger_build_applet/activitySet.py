import simplejson
import os
from github import Github, GithubException

class ActivitySet(object):
    def __init__(self, user, repo, activitySet_id, cname=None, prefLabel="", altLabel="",
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
                "@type": "https://www.repronim.org/schema-standardization/schemas/ActivitySet.jsonld",
                "schema:schemaVersion": "0.0.1",
                "schema:version": "0.0.1",
            }
        self.data['@id'] = activitySet_id
        self.data["skos:prefLabel"] = prefLabel
        self.data["skos:altLabel"] = altLabel
        self.data["schema:description"] = description
        self.data['variableMap'] = []
        self.data["ui"] = dict(shuffle=shuffle, allow=allow, order=[], visibility={}, activity_display_name={})

        self.extra_context = {
            '@context': {
                "@version": 1.1,
            }
        }

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
    
    def toJSON(self):
        return simplejson.dumps(self.data)

    def addActivity(self, activity, displayName, visibility=True):
        # TODO: make sure item is of type Activity
        activity_url = activity.postActivity()

        # TODO: make sure the item isn't already in the variableMap
        self.data['variableMap'].append({
            "variableName": activity.data['@id'],
            "isAbout": activity.data['@id'],
        })
        self.data['ui']['visibility'][activity.data['@id']] = visibility
        self.data['ui']['activity_display_name'][activity.data['@id']] = displayName
        # TODO: make sure the item isn't already in the context
        self.extra_context['@context'][activity.data['@id']] = {
            '@id': activity_url,
            '@type': '@id',
        }

        # TODO: make sure the item isn't already in the list
        self.data['ui']['order'].append(activity.data['@id'])

    
    def postActivitySetContext(self):
        """
        
        """
        fid = self.data['@id']
        try:
            self.gh_repo.create_file("/activitySets/{}/{}_context.jsonld".format(fid, fid), 
                            "updated {}/{}_context".format(fid, fid),
                            simplejson.dumps(self.extra_context),
                            branch="master")
        except GithubException:
            filen = self.gh_repo.get_file_contents("/activitySets/{}/{}_context.jsonld".format(fid, fid))
            self.gh_repo.update_file("/activitySets/{}/{}_context.jsonld".format(fid, fid), 
                            "updated {}/{}_context".format(fid, fid), simplejson.dumps(self.extra_context),
                            filen.sha)
        
        if not self.cname:
            url = "https://{user}.github.io/{repo}/activitySets/{fid}/{fid}_context.jsonld".format(user=self.user,
                                                                           repo=self.repo,
                                                                           fid=fid)
        else:
            url = "https://{cname}/{repo}/activitySets/{fid}/{fid}_context.jsonld".format(
                                                                cname=self.cname,
                                                                repo=self.repo,
                                                                fid=fid)
        return url


    def postActivitySet(self):
        # 1. post the extra context
        context_url = self.postActivitySetContext()


        # 2. update self.data.context with URL
        self.data['@context'].append(context_url)

        # 3. post self.data into the activities folder
        fid = self.data['@id']
        try:
            self.gh_repo.create_file("/activitySets/{}/{}_schema.jsonld".format(fid, fid), 
                            "updated {}/{}".format(fid, fid), self.toJSON(),
                            branch="master")
        except GithubException:
            filen = self.gh_repo.get_file_contents("/activitySets/{}/{}_schema.jsonld".format(fid,fid))
            self.gh_repo.update_file("/activitySets/{}/{}_schema.jsonld".format(fid, fid), 
                            "updated {}/{}".format(fid,fid), self.toJSON(),
                            filen.sha)
        
        if not self.cname:
            url = "https://{user}.github.io/{repo}/activitySets/{fid}/{fid}_schema.jsonld".format(user=self.user,
                                                                           repo=self.repo,
                                                                           fid=fid)
        else:
            url = "https://{cname}/{repo}/activitySets/{fid}/{fid}_schema.jsonld".format(cname=self.cname,
                                                                repo=self.repo,
                                                                fid=fid)
        return url
        