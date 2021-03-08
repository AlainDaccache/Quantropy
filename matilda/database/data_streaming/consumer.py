from kafka.consumer import KafkaConsumer
from json import loads
from mongoengine import *

from matilda.database import object_model


consumer = KafkaConsumer(
    'numtest',  # kafka topic
    bootstrap_servers=['localhost:9092'],  # same as our producer
    # It handles where the consumer restarts reading after breaking down or being turned off and can be set either
    # to earliest or latest. When set to latest, the consumer starts reading at the end of the log.
    # When set to earliest, the consumer starts reading at the latest committed offset.
    auto_offset_reset='earliest',
    enable_auto_commit=True,  # makes sure the consumer commits its read offset every interval.
    # join a consumer group for dynamic partition assignment and offset commits
    # a consumer needs to be part of a consumer group to make the auto commit work.
    # otherwise, need to do it manually i.e. consumer.assign([TopicPartition('foobar', 2)]); msg = next(consumer)
    group_id='my-group',
    # deserialize encoded values
    value_deserializer=lambda x: loads(x.decode('utf-8')))


def get_atlas_db_url(username, password, dbname):
    return f"mongodb+srv://{username}:{password}@cluster0.ptrie.mongodb.net/{dbname}?retryWrites=true&w=majority&" \
           f"ssl=true"


atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
db = connect(host=atlas_url)

# The consumer iterator returns ConsumerRecords, which are simple namedtuples
# that expose basic message attributes: topic, partition, offset, key, and value:
for message in consumer:
    message = message.value
    print(message)
    object_model.Test(number=message['number']).save()
    print('{} added to db'.format(message))

# # Then to check whats in it:
# for doc in object_model.Test.objects:
#     print(doc._data)
