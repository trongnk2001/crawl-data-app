import os
import time
import json
from confluent_kafka import Consumer, KafkaError

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = os.getenv('OUTPUT_TOPIC', 'output-topic')
GROUP_ID = os.getenv('GROUP_ID', 'python-consumer-group')
WAIT_FOR_KAFKA = os.getenv('WAIT_FOR_KAFKA', 'false').lower() == 'true'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'socket.timeout.ms': 10000,
    'session.timeout.ms': 10000,
    'max.poll.interval.ms': 30000,
    'fetch.wait.max.ms': 500
}


def wait_for_kafka():
    """Đợi Kafka sẵn sàng"""
    if not WAIT_FOR_KAFKA:
        return True

    from confluent_kafka import admin
    a = admin.AdminClient({'bootstrap.servers': KAFKA_BROKER})

    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            topics = a.list_topics(timeout=5)
            if TOPIC in topics.topics:
                print(f"Topic {TOPIC} is ready!")
                return True
            print(
                f"Waiting for topic {TOPIC}... (attempt {retry_count + 1}/{max_retries})")
            retry_count += 1
            time.sleep(5)
        except Exception as e:
            print(
                f"Waiting for Kafka... (attempt {retry_count + 1}/{max_retries}) Error: {e}")
            retry_count += 1
            time.sleep(5)

    raise Exception(f"Failed to find topic {TOPIC} after multiple attempts")


def consume_messages():
    if not wait_for_kafka():
        return

    consumer = Consumer(conf)
    consumer.subscribe([TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print(f"Reached end of partition {msg.partition()}")
                else:
                    print(f"Consumer error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                print(
                    f"Received message (partition {msg.partition()}, offset {msg.offset()}):")
                print(json.dumps(data, indent=2))
            except Exception as e:
                print(f"Error processing message: {e}")

    except KeyboardInterrupt:
        print("Consumer interrupted")
    finally:
        consumer.close()
        print("Consumer closed")


if __name__ == "__main__":
    print(f"Starting consumer for topic: {TOPIC}")
    try:
        consume_messages()
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)
