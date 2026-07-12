from time import sleep
from kafka.producer import KafkaProducer
import json

producer = KafkaProducer(
    # set host and port that producer should contact to bootstrap initial cluster metadata
    bootstrap_servers=['localhost:9092'],
    # how data should be serialized before sending to broker (convert the data to a json file and encode it to utf-8)
    value_serializer=lambda x: json.dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number': e}  # key:value pairs to send (nb: this is not the topic key). Use a key for hashed-partitioning
    future = producer.send('numtest', value=data)

    # How to make sure the message is received by the broker?
    print(f'sent {data}')
    sleep(5)  # option 1: take a break

    # result = future.get(timeout=60)  # option 2: block until a single message is sent (or timeout)
    # option 3: Block until all pending messages are at least put on the network. This does not guarantee delivery
    # or success! It is really. Only useful if you configure internal batching using linger_ms
    # producer.flush()
