import copy
import json
import os
import urllib

from github import Github, GithubException


class BaseNode(object):
    """
    Base class for any JSONLD node with a URI.
    """
    default_init_data = {}
    set_data_mapping = {}
    node_id = None
    data = None

    def __init__(self, node_id, **kwargs):
        self.node_id = node_id
        for item in ['storage', 'base_uri', 'uri']:
            if item in kwargs:
                setattr(self, item, kwargs[item])

        # Read and load existing data if available, or load default.
        self.set_init_data()

    def get_path(self):
        """
        Get the node's path. The full URI combines base URI with this.
        """
        raise NotImplementedError

    def set_init_data(self):
        """
        If there is a storage, try to initialize with existing data.

        TODO: Validate result and abort
        """
        if hasattr(self, 'storage'):
            data = self.storage.read(self)
            if data:
                self.data = data

        # TODO: Reset self.data if it doesn't successfully validate?
        if not self.data:
            self.data = self.get_default_data()


    def get_default_data(self):
        """
        Override in child classes to extend parent class defaults.
        """
        return self.default_init_data.copy()

    def get_set_data_mapping(self):
        """
        Override in child classes to extend parent class defaults.
        """
        return self.set_data_mapping

    def set_data(self, **kwargs):
        data_mapping = self.get_set_data_mapping()
        for item in data_mapping:
            jsonld_key = data_mapping[item][0]
            jsonld_default_value = data_mapping[item][1]
            if item in kwargs:
                self.data[jsonld_key] = kwargs[item]
            elif jsonld_key not in self.data:
                self.data[jsonld_key] = copy.copy(jsonld_default_value)

    def get_uri(self):
        """
        Return node's URI, if possible.
        """
        if hasattr(self, 'uri'):
            return self.uri
        elif hasattr(self, 'base_uri'):
            return urllib.parse.urljoin(self.base_uri, self.get_path())
        else:
            raise NotImplementedError("Full URI can't be generated when base URI isn't set.")

    def get_data(self):
        """
        Return node's data. Override to add adding URIs for linked data items.
        """
        return self.data

    def get_json(self):
        """
        Return the JSON data for the node.
        """
        return json.dumps(self.get_data())

    def write(self, comment=""):
        """
        Write the node's data to storage.
        """
        if hasattr(self, "storage"):
            self.storage.write(self)
        else:
            raise NotImplementedError("Storage must be set to write node data.")

    def validate(self):
        """
        Implement node validation here.
        """
        raise NotImplementedError


class Storage(object):
    """
    Base Storage class for reading and writing content.

    Storage classes are expected to implement the 'read' and 'write' function.
    """
    def __init__(self):
        return

    def read(self, node, comment=''):
        raise NotImplementedError("""The read method isn't implemented in this Storage.""")

    def write(self, node, comment=''):
        raise NotImplementedError("""The read method isn't implemented in this Storage.""")


class LocalStorage(Storage):
    """
    Writes locally, uses url_base to return anticipated location for linked content.
    """
    def __init__(self, local_dir='.'):
        self.local_dir = local_dir

    def get_full_path(self, node):
        full_path = os.path.join(self.local_dir, node.get_path())

    def read(self, node):
        # TODO: implement this, currently behaves as if blank.
        return None

    def write(self, node, comment=''):
        full_path = os.path.join(self.local_dir, node.get_path())
        target_dir = os.path.dirname(full_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(full_path, 'w') as f:
            f.write(node.get_json())


class GitHubStorage(Storage):
    def __init__(self, user, repo, cname=None):
        self.cname = cname
        self.github = Github(os.environ['GH_TOKEN'])
        self.user = user

        if self.cname:
            self.url_base = "https://{cname}/{repo}/"
        else:
            self.url_base = "https://{user}.github.io/{repo}/"

        self.repo = self.github.get_repo(
            "{user}/{repo}".format(user=self.user, repo=self.repo))

    def read(self, node):
        # TODO: implement this, currently behaves as if blank.
        return None

    def write(self, node, comment=""):
        try:
            self.repo.create_file(path, comment, content, branch="master")
        except GithubException:
            filen = repo.get_file_contents(path)
            repo.update_file(path, comment, content, filen.sha)
        return urllib.parse.urljoin(self.url_base, path)