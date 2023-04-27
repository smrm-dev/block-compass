from flask.views import MethodView
from flask import request, jsonify, json

from traceback import print_exc


class Blocks(MethodView):
    def get(self):

        try: 
            params = request.args.to_dict()
            timestamp = params['timestamp']
            chain_ids = params.get('chain_ids')

            if chain_ids is None:
                ## TODO: should get all supported chains
                chain_ids = [1,2,3]
            else:
                chain_ids = json.loads(chain_ids)


            blocks = {}
            for chain_id in chain_ids:
                ## TODO: should query db
                blocks[chain_id] = get_block_by_timestamp(timestamp, chain_id)

            return jsonify(success=True, blocks=blocks), 200

        except Exception as e:
            print_exc()
            return jsonify(success=False, message='Bad Request!'), 400

def get_block_by_timestamp(timestamp, chain_id):
    return timestamp