from sawtooth_sdk.processor.core import TransactionProcessor
from dataquality.processor.handler import DQTransactionHandler

def main():
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://validator-bgx-с1-1:4104')

    handler = DQTransactionHandler()

    processor.add_handler(handler)

    processor.start()