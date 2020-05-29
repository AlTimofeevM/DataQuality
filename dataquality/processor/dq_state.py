import hashlib
from sawtooth_sdk.processor.exceptions import InternalError

DQ_NAMESPACE = hashlib.sha512('dataquality='.encode("utf-8")).hexdigest()[0:6]

def _make_dq_address(name):
    return DQ_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

class Quality:
    def __init__(self, name, time, open, high, low, close, volume):
        self.name = name
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class DQState:

    TIMEOUT = 3

    def __init__(self, context):
        self._context = context
        self._address_cache = {}

    def delete_quality(self, name):
        qualities = self._load_qualities(name=name)

        del qualities[name]
        if qualities:
            self._store_quality(name, qualities=qualities)
        else:
            self._delete_quality(name)

    def set_quality(self, name, quality):
        qualities = self._load_qualities(name=name)

        qualities[name] = quality

        self._store_quality(name, qualities=qualities)

    def get_quality(self, name):
        return self._load_qualities(name=name).get(name)

    def _store_quality(self, name, qualities):
        address = _make_dq_address(name)

        state_data = self._serialize(qualities)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _delete_quality(self, name):
        address = _make_dq_address(name)

        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)

        self._address_cache[address] = None

    def _load_qualities(self, name):
        address = _make_dq_address(name)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_qualities = self._address_cache[address]
                qualities = self._deserialize(serialized_qualities)
            else:
                qualities = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                qualities = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                qualities = {}

        return qualities

    def _deserialize(self, data):
        qualities = {}
        try:
            for quality in data.decode().split("|"):
                name, time, open, high, low, close, volume = quality.split(",")

                qualities[name] = quality(name, time, open, high, low, close, volume)
        except ValueError:
            raise InternalError("Failed to deserialize quality data")

        return qualities

    def _serialize(self, qualities):
        quality_strs = []
        for name, q in qualities.items():
            quality_str = ",".join(
                [name, q.time, q.open, q.high, q.low, q.close, q.volume])
            quality_strs.append(quality_str)

        return "|".join(sorted(quality_strs)).encode()