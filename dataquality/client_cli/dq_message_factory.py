from sawtooth_processor_test.message_factory import MessageFactory


class DQMessageFactory:
    def __init__(self, signer=None):
        self._factory = MessageFactory(
            family_name="dq",
            family_version="1.0",
            namespace=MessageFactory.sha512("dq".encode("utf-8"))[0:6],
            signer=signer)

    def _quality_to_address(self, quality):
        return self._factory.namespace + \
            self._factory.sha512(quality.encode())[0:64]

    def create_tp_register(self):
        return self._factory.create_tp_register()

    def create_tp_response(self, status):
        return self._factory.create_tp_response(status)

    def _create_txn(self, txn_function, quality, action):
        payload = ",".join([
            str(quality), str(action)
        ]).encode()

        addresses = [self._quality_to_address(quality)]

        return txn_function(payload, addresses, addresses, [])

    def create_tp_process_request(self, action, quality):
        txn_function = self._factory.create_tp_process_request
        return self._create_txn(txn_function, quality, action)

    def create_transaction(self, quality, action):
        txn_function = self._factory.create_transaction
        return self._create_txn(txn_function, quality, action)

    def create_get_request(self, quality):
        addresses = [self._quality_to_address(quality)]
        return self._factory.create_get_request(addresses)

    # def create_get_response(
    #     self, game, board="---------", state="P1-NEXT", player1="", player2=""
    # ):
    #     address = self._game_to_address(game)
    #
    #     data = None
    #     if board is not None:
    #         data = ",".join([game, board, state, player1, player2]).encode()
    #     else:
    #         data = None
    #
    #     return self._factory.create_get_response({address: data})
    #
    # def create_set_request(
    #     self, game, board="---------", state="P1-NEXT", player1="", player2=""
    # ):
    #     address = self._game_to_address(game)
    #
    #     data = None
    #     if state is not None:
    #         data = ",".join([game, board, state, player1, player2]).encode()
    #     else:
    #         data = None
    #
    #     return self._factory.create_set_request({address: data})

    def create_set_response(self, quality):
        addresses = [self._quality_to_address(quality)]
        return self._factory.create_set_response(addresses)

    def get_public_key(self):
        return self._factory.get_public_key()