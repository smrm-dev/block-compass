from flask.views import MethodView
from flask import request, jsonify, json

from traceback import print_exc

from block_compass.db import get_block_number_by_timestamp, get_chains, get_genesis_block_timestamp


class Blocks(MethodView):
    def get(self):

        try: 
            params = request.args.to_dict()
            timestamp = int(params['timestamp'])
            chain_ids = params.get('chain_ids')

            if chain_ids is None:
                chain_ids = [chain['id'] for chain in get_chains()]
            else:
                chain_ids = json.loads(chain_ids)

            blocks = {}
            for chain_id in chain_ids:
                if timestamp < get_genesis_block_timestamp(chain_id):
                   blocks[chain_id] = 'TIMESTAMP_OUT_OF_RANGE' 
                else:
                    blocks[chain_id] = get_block_number_by_timestamp(timestamp, chain_id)

            return jsonify(success=True, blocks=blocks), 200

        except Exception as e:
            print_exc()
            return jsonify(success=False, message='Bad Request!'), 400