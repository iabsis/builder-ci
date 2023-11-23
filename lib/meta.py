import lib.db as db
import lib.logs as logs
import lib.db as db
from datetime import datetime


class Meta():

    def __init__(self, id):
        self.id = id
        try:
            self.meta = db.getBuilds(self.id)["meta"]
        except KeyError:
            self.meta = {}

    def __getitem__(self, attribute):
        try:
            result = self.meta[attribute]
        except KeyError:
            if attribute == "name":
                return db.getName(self.id)
            logs.warning("Meta requested doesn't exist: " + attribute)
            result = None

        return result

    def __setitem__(self, attribute, data):
        self.meta[attribute] = data

    def saveMeta(self):
        db.setMeta(self.id, self.meta)

    def mergeMeta(self, meta):
        for key, value in meta.items():
            self.meta[key] = value
