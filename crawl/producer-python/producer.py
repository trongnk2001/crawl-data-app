import os
import time
import json
from confluent_kafka import Producer, KafkaException

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = os.getenv('INPUT_TOPIC', 'input-topic')
WAIT_FOR_KAFKA = os.getenv('WAIT_FOR_KAFKA', 'false').lower() == 'true'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'python-producer',
    'message.timeout.ms': 10000,
    'socket.timeout.ms': 10000,
    'socket.keepalive.enable': True,
    'log.connection.close': False
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
            a.list_topics(timeout=5)
            print("Kafka is ready!")
            return True
        except Exception as e:
            print(
                f"Waiting for Kafka... (attempt {retry_count + 1}/{max_retries}) Error: {e}")
            retry_count += 1
            time.sleep(5)

    raise Exception("Failed to connect to Kafka after multiple attempts")


def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(
            f'Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')


def produce_messages():
    if not wait_for_kafka():
        return

    producer = Producer(conf)

    try:
        for i in range(1, 1001):
            data = {
                "id": i,
                "timestamp": int(time.time()),
                "value": i * 10,
                "message": f"Sample message {i}"
            }

            try:
                producer.produce(
                    topic=TOPIC,
                    key=str(i),
                    value=json.dumps(data),
                    callback=delivery_report
                )
                producer.flush()
                print(f"Produced: {data}")
                time.sleep(1)
            except BufferError as e:
                print(f"Buffer error: {e}, retrying...")
                time.sleep(1)
                continue
            except KafkaException as e:
                print(f"Kafka exception: {e}, retrying...")
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("Producer interrupted")
    finally:
        producer.flush()
        print("Producer closed")


if __name__ == "__main__":
    print(f"Starting producer for topic: {TOPIC}")
    try:
        produce_messages()
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)
