from sawtooth_sdk.processor.core import TransactionProcessor
from dataquality.processor.handler import DataQualityTransactionHandler

def main():
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://127.0.0.1:4004')

    handler = DataQualityTransactionHandler()

    processor.add_handler(handler)

    processor.start()