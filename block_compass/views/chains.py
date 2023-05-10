from flask.views import MethodView
from flask import request, jsonify, json

from traceback import print_exc

from block_compass.db import get_chains


class Chains(MethodView):
    def get(self):

        try: 
            chains = get_chains()
            
            result = []
            for chain in chains:
                result.append({
                    'id': chain['id'],
                    'name': chain['name']
                })

            return jsonify(success=True, chains=result), 200

        except Exception as e:
            print_exc()
            return jsonify(success=False, message='Bad Request!'), 400