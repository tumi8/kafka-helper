import asyncio
import fastavro
import io
import kafka
import time


class KafkaProducerContextManager:
    __slots__ = ('config', 'producer', 'buffer', 'lock')

    def __init__(self, **config):
        self.config = config
        self.producer = None
        self.buffer = io.BytesIO()
        self.lock = asyncio.locks.Lock()

    def __enter__(self):
        errors = 0
        while not self.producer:
            try:
                self.producer = kafka.KafkaProducer(**self.config)
            except kafka.errors.NoBrokersAvailable as e:
                errors += 1
                if errors >= 3:
                    raise e
                time.sleep(3)
        return self

    def __exit__(self, *args):
        self.producer.close()
        self.buffer.close()

    def write(self, value, topic):
        future = self.producer.send(topic, value=value)
        future.get(timeout=20)

    def write_avro(self, value, schema, topic):
        fastavro.writer(self.buffer, schema, value)
        raw_bytes = self.buffer.getvalue()
        future = self.producer.send(topic, value=raw_bytes)
        try:
            future.get(timeout=20)
        finally:
            self.buffer.seek(0)
            self.buffer.truncate(0)


class KafkaConsumerContextManager:
    __slots__ = ('config', 'topics', 'consumer', 'buffer')

    def __init__(self, *topics, **config):
        self.config = config
        self.topics = topics
        self.consumer = None
        self.buffer = io.BytesIO()

    def __enter__(self):
        errors = 0
        while not self.consumer:
            try:
                self.consumer = kafka.KafkaConsumer(*self.topics, **self.config)
            except kafka.errors.NoBrokersAvailable as e:
                errors += 1
                if errors >= 3:
                    raise e
                time.sleep(3)
        return self

    def __exit__(self, *args):
        self.consumer.close()
        self.buffer.close()

    def avro_messages(self, schema, batched=False):
        for message in self.consumer:
            self.buffer.write(message.value)
            self.buffer.seek(0)
            reader = fastavro.reader(self.buffer, schema)
            if batched:
                yield reader
            else:
                for record in reader:
                    yield record

            self.buffer.seek(0)
            self.buffer.truncate(0)


__all__ = ['KafkaProducerContextManager', 'KafkaConsumerContextManager']

