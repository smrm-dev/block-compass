from flask.views import MethodView
from flask import request, jsonify, json

from traceback import print_exc

from block_compass.db import get_block_by_timestamp


class Blocks(MethodView):
    def get(self):

        try: 
            params = request.args.to_dict()
            timestamp = int(params['timestamp'])
            chain_ids = params.get('chain_ids')

            if chain_ids is None:
                ## TODO: should get all supported chains
                chain_ids = [1] 
            else:
                chain_ids = json.loads(chain_ids)

            blocks = {}
            for chain_id in chain_ids:
                blocks[chain_id] = get_block_by_timestamp(timestamp, chain_id)['number']

            return jsonify(success=True, blocks=blocks), 200

        except Exception as e:
            print_exc()
            return jsonify(success=False, message='Bad Request!'), 400