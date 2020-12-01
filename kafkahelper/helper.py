import asyncio
import fastavro
import io
import kafka


class KafkaProducerContextManager:
    __slots__ = ('config', 'producer', 'buffer', 'lock')

    def __init__(self, **config):
        self.config = config
        self.producer = None
        self.buffer = io.BytesIO()
        self.lock = asyncio.locks.Lock()

    def __enter__(self):
        self.producer = kafka.KafkaProducer(**self.config)
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

    async def write_async(self, value, topic):
        async with self.lock:
            future = self.producer.send(topic, value=value)
            future.get(timeout=20)

    async def write_avro_async(self, value, schema, topic):
        fastavro.writer(self.buffer, schema, value)
        raw_bytes = self.buffer.getvalue()
        async with self.lock:
            try:
                future = self.producer.send(topic, value=raw_bytes)
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
        self.consumer = kafka.KafkaConsumer(*self.topics, **self.config)
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

