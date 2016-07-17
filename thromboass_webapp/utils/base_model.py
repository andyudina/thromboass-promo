from django.db import models

class JSONMixin(object):
    def to_json(self):
        json_ = self.__dict__.copy()
        del json_['_state']  # Deleting standard django model _state field with meta information
        for key in json_.keys(): 
            # Delete cached fields, m2m fields and datetime
            if 'cache' in key or 'relevant' in key or 'created_at' in key: del json_[key]
            # get path for images
            elif hasattr(json_[key], 'path'): json_[key] = json_[key].path
            # delete fk
            elif isinstance(json_[key], models.Model): del json_[key]
        return json_
