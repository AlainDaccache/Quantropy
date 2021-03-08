"""

Step 1: Install JRE.
    - To make sure it's installed, go to command line and write 'java -version'.

Step 2: Install and configure Apache Zookeeper.
    - https://zookeeper.apache.org/releases.html#download. Make sure you download the binary files (bin) and not the source.
    - Create data directory in zookeeper folder i.e. mkdir data
    - In ./conf, copy and rename zoo_sample.cfg to zoo.cfg, and edit 'dataDir' so points to your data dir i.e. ../data
                You can change the default port if you want. For now, we make it run default localhost:2181.
    - In Environment variable System:   Add ZOOKEEPER_HOME = your path to zookeeper
                                        Edit System Variable named “Path” and append ;%ZOOKEEPER_HOME%\bin;
    - Start Zookeeper: Open command prompt and type zkserver, which will start zookeeper on the default server.
        For now it doesn't work so i do :   cd C:\Tools\apache-zookeeper-3.6.2-bin\bin
                                            zkServer.cmd
Step 3: Install and configure Apache Kafka.

    - https://kafka.apache.org/downloads. Make sure you download the binary files (bin) and not the source.
        Make sure you extract it somewhere where the path isn't long. When i did to Downloads, eventually
        I got an error that the command cannot be read since input line was long. I created uner C:// a
        directory called 'Tools'.

    - In the config folder, in server.properties, change logs.dirs to point to your-kafka-path/kafka-logs
        In my case: log.dirs=C:\\Tools\\kafka_2.13-2.7.0\\kafka-logs
    - If you changed zookeeper's port, then change the zookeeper.connect=localhost:2181 property

    - Start Broker: Open another command prompt, go to your kafka directory, and type:
        .\bin\windows\kafka-server-start.bat .\config\server.properties
        By default, Kafka broker runs on localhost: 9092.

Step 4: Creating Topic:
    - a topic is similar to a folder in a filesystem, and the events are the files in that folder. To create a topic:
    - Open another command prompt, cd into your kafka dir, then type:
        .\bin\windows\kafka-topics.bat --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic sql-insert

    This creates a topic called 'sql-insert'

Step 5: Producer and Consumer
    - To write some events into the topic, do the following (make sure you're in your kafka dir)
        .\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic sql-insert

        By default, each line you enter will result in a separate event being written to the topic.
        > This is my first event
        > This is my second event
        You can stop the producer client with Ctrl-C at any time.
    - The Consumer listens to the Broker (and not to Zookeeper) to read the events.
        Open a new terminal, cd into kafka dir, and type:
        .\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic sql-insert
    - Now you can write some events in the producer terminal, and see consumer client read the events you just created:

When ready to terminate the environment, Ctrl-C to stop each of Zookeeper, Kafka, Producer, and Consumer.

"""
from time import sleep
from json import dumps
from kafka.producer import KafkaProducer

producer = KafkaProducer(
    # set host and port that producer should contact to bootstrap initial cluster metadata
    bootstrap_servers=['localhost:9092'],
    # how data should be serialized before sending to broker (convert the data to a json file and encode it to utf-8)
    value_serializer=lambda x: dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number': e}  # key:value pairs to send (nb: this is not the topic key). Use a key for hashed-partitioning
    future = producer.send('numtest', value=data)

    # How to make sure the message is received by the broker?

    sleep(5)  # option 1: take a break
    print(f'sent {data}')
    # result = future.get(timeout=60)  # option 2: block until a single message is sent (or timeout)
    # option 3: Block until all pending messages are at least put on the network. This does not guarantee delivery
    # or success! It is really. Only useful if you configure internal batching using linger_ms
    # producer.flush()
