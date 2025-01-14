import json
from .producer import get_producer
from .consumer import get_consumer


async def send_message(topic, data, producer=None):
    producer = producer if producer else await get_producer()
    try:
        await producer.send_and_wait(
            topic, json.dumps(data).encode("ascii")
        )
    finally:
        await producer.stop()


def pipe(topic_input, topic_output=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            print(f"{topic_input} started.")
            kafka_consumer = await get_consumer(topic_input)
            try:
                async for message in kafka_consumer:
                    value = json.loads(message.value.decode())
                    data = await func(value, *args, **kwargs)
                    if data and topic_output:
                        await send_message(topic_output, data)
            finally:
                await kafka_consumer.stop()
        return wrapper
    return decorator
