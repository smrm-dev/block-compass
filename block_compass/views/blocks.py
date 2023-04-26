from flask.views import MethodView
from flask import request, jsonify, json

from traceback import print_exc


class Blocks(MethodView):
    def get(self):
        return 'Ok', 200