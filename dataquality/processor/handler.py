import requests
import math
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

from dataquality.processor.dq_payload import DQPayload
from dataquality.processor.dq_state import Quality
from dataquality.processor.dq_state import DQState
from dataquality.processor.dq_state import DQ_NAMESPACE

LOGGER = logging.getLogger(__name__)

class DQTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return 'dq'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [DQ_NAMESPACE]

    def apply(self, transaction, context):

        header = transaction.header
        signer = header.signer_public_key

        dq_payload = DQPayload.from_bytes(transaction.payload)

        dq_state = DQState(context)

        if dq_payload.action == 'delete':
            quality = dq_state.get_quality(dq_payload.name)

            if quality is None:
                raise InvalidTransaction(
                    'Invalid action: quality does not exist')

            dq_state.delete_quality(dq_payload.name)

        elif dq_payload.action == 'create':

            if dq_state.get_quality(dq_payload.name) is not None:
                raise InvalidTransaction(
                    'Invalid action: Quality already exists: {}'.format(
                        dq_payload.name))

            response = requests.get(
                'https://cryptodatum.io/api/v1/candles/?symbol=bitfinex:btcusd&type=tick&step=100&limit=1&start=1364923374000000000&end=1364948040000000000&format=json',
                headers={'Authorization': 'CriptoDatum-API-key'},
            )
            json_response = response.json()

            quality = Quality(name=dq_payload.name,
                            time = json_response['values'][0],
                            open = json_response['values'][1],
                            high = json_response['values'][2],
                            low = json_response['values'][3],
                            close = json_response['values'][4],
                            valume = json_response['values'][5])
            dq_state.set_quality(dq_payload.name, quality)
            _display("User {} created a quality.".format(signer[:6]))

        elif dq_payload.action == 'check':
            quality = dq_state.get_quality(dq_payload.name)

            if quality is None:
                raise InvalidTransaction(
                    'Invalid action: Take requires an existing quality')

            if quality.time >= 1364948040000000000:
                raise InvalidTransaction(
                    'No data available')

            newJson = requests.get(
                'https://cryptodatum.io/api/v1/candles/?symbol=bitfinex:btcusd&type=tick&step=100&limit=1&start=' + str(quality.time + 120000000000) + '&end=1364948040000000000&format=json',
                headers={'Authorization': 'CriptoDatum-API-key'},
            ).json()
            q = abs(math.log(quality.close) - math.log(newJson['values'][4]))
            if (q >= 0.2):
                raise InvalidTransaction(
                    'Data of poor quality, recording denied')                                                                                                                           
            else:
                quality.time = newJson['values'][0],
                quality.open = newJson['values'][1],
                quality.high = newJson['values'][2],
                quality.low = newJson['values'][3],
                quality.close = newJson['values'][4],
                quality.valume = newJson['values'][5]

            dq_state.set_quality(dq_payload.name, quality)
            _display(
                "User {}\n\n".format(
                    signer[:6]))

        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                dq_payload.action))

def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")