#!/bin/env python3
import argparse
import json
import logging
import sdnotify
import sys
import time
from threading import Thread, Event, Lock
from kafkahelper import KafkaProducerContextManager


def main():
    parser = argparse.ArgumentParser(description='Write from stdin to kafka topic')
    parser.add_argument('-t', '--topic', type=str, help='The kafka topic to observe',required=True)
    parser.add_argument('-s', '--kafka-server', type=str, help='kafka server')
    parser.add_argument('-u', '--kafka-username', type=str, help='kafka username')
    parser.add_argument('-p', '--kafka-password', type=str, help='password for the kafka user')
    parser.add_argument('-l', '--message-list', action='store_true', help='message contains a list which item each should go in a separate row')
    parser.add_argument('-i', '--intervall', type=int, default=1, help='Seconds waited until new message list is send')
    parser.add_argument('-n', '--max-list-size', type=int, default=10, help='Maximum amount of entries per list message')
    parser.add_argument('-a', '--avro', nargs=2, metavar=('MODULE', 'SCHEMA'), type=str, help='Set avro schema if message is an avro message')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='enable debug logging. -vv enables also kafka debug logging')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose > 0 else logging.INFO,
                        format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

    if args.verbose == 1:
        for name in logging.root.manager.loggerDict:
            if name.startswith('kafka.'):
                kafka_logger = logging.getLogger(name)
                kafka_logger.setLevel(logging.INFO)

    try:
        if args.kafka_username is not None and args.kafka_password is not None:
            with KafkaProducerContextManager(bootstrap_servers=[args.kafka_server],
                                                    security_protocol="SASL_PLAINTEXT",
                                                    sasl_plain_username=args.kafka_username,
                                                    sasl_plain_password=args.kafka_password,
                                                    sasl_mechanism="PLAIN",
                                                    max_request_size=4194304) as producer:
                write_messages(args, producer)
        else:
            with KafkaProducerContextManager(bootstrap_servers=[args.kafka_server],
                                                    max_request_size=4194304) as producer:    
                write_messages(args, producer)     
    except KeyboardInterrupt:
        logging.error('stopping due to keyboard interrupt')

    shutting_down.set()


# Global variables - Shared in multiple Threads 
list_lock = Lock()
shutting_down = Event()
message_list = []
time_of_last_message = None
written_messages = 0


def write_messages(args, producer):
    """
    Reads lines from stdin and transforms them to messages in kafka
    """
    global time_of_last_message
    
    systemd_notifier = sdnotify.SystemdNotifier()
    systemd_notifier.notify('READY=1')

    logging_thread = Thread(target=log_process, args=(args.verbose,))
    logging_thread.setDaemon(True)
    logging_thread.start()

    if args.avro: 
        # Load AVRO schema
        config_schema = __import__(args.avro[0], fromlist=[args.avro[1]])
        schema = getattr(config_schema, args.avro[1])
    else: 
        schema = None

    if args.message_list:
        # Starting Thread for message lists
        time_of_last_message = time.monotonic()  
        time_keeper_thread = Thread(target=write_after_timeout, args=(args, producer, schema,))
        time_keeper_thread.start()

    for line in sys.stdin:
        # Read message from stdin
        systemd_notifier.notify('WATCHDOG=1')
        #logging.debug('read line: %s',line.strip())

        # Send message to Kafka
        if not args.message_list:
            
            # Not Batched, every line one kafka message
            if args.avro:
                producer.write_avro([json.loads(line.strip())], schema, args.topic)
            else :
                producer.write(bytes(line.strip(), 'utf-8'), args.topic)
                
            #logging.debug('message send to kafka topic %s',args.topic)
            global written_messages
            written_messages += 1
        else:

            # Message List -> Batched, multiple lines one Kafka Messages
            with list_lock:
                message_list.append(json.loads(line.strip()))

            if len(message_list) >= args.max_list_size:
                time_of_last_message = write_list(args, producer, schema)
            # time_keeper_thread ensures that list message is written after specified time if not enough messages are read received
    
    # All lines read, terminating gently
    shutting_down.set()
    if args.message_list:
        time_keeper_thread.join()


def write_after_timeout(args, producer, schema):
    """
    Ensures that a not empty message list is send after the specified time.
    """
    global time_of_last_message

    # Loop that checks if time is elapsed
    while True:
        if shutting_down.is_set():
            # Stopping gently, sending remaining entries in list
            time_of_last_message = write_list(args, producer, schema)
            return

        if time.monotonic() - time_of_last_message >= args.intervall:
            # Time-Intervall since last send kafka message is elapsed -> sending message
            time_of_last_message = write_list(args, producer, schema)

        # Waiting until next check    
        time.sleep(0.5)


def write_list(args, producer, schema) -> float:
    """
    Writes the list message to the kafka topic
    """
    with list_lock: 
        if message_list:
            # List is not empty -> sending it
            if args.avro:
                # Sending encoded as AVRO
                producer.write_avro(message_list, schema, args.topic)
            else: 
                # Sending as JSON list
                producer.write(bytes(json.dumps(message_list), 'utf-8'), args.topic)  
            #logging.debug('message list with %d entries send to kafka topic %s', len(message_list), args.topic)
            global written_messages
            written_messages += len(message_list)
            message_list.clear()
    return time.monotonic()


def log_process(verbose):
    """
    If logging verbose, prints the number of processed messages of the last period every 5 minutes
    """
    global written_messages
    while verbose and written_messages >= 0:
        logging.debug('Wrote %d messages to kafka in last 5 min', written_messages)
        written_messages = 0
        time.sleep(60*5)

if __name__ == '__main__':
    main()