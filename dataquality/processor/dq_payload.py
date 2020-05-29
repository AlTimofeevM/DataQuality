from sawtooth_sdk.processor.exceptions import InvalidTransaction

class DQPayload:
    def __init__(self, payload):
        try:
            name, action = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not name:
            raise InvalidTransaction('Name is required')

        if '|' in name:
            raise InvalidTransaction('Name cannot contain "|"')

        if not action:
            raise InvalidTransaction('Action is required')

        if action not in ('create', 'check', 'delete'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        self._name = name
        self._action = action

    @staticmethod
    def from_bytes(payload):
        return DQPayload(payload=payload)

    @property
    def name(self):
        return self._name

    @property
    def action(self):
        return self._action
