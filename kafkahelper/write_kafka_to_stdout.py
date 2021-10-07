#!/bin/env python3
import argparse
import json
import logging
import sdnotify
import sys
from kafkahelper import KafkaConsumerContextManager


def main():
    example_usage = '''example: 

 python write_kafka_to_stdout.py -s localhost:9092 -t myTopic -g myGroup -l
 python write_kafka_to_stdout.py -s localhost:9092 -t myTopic -g myGroup -u myUser -p myPassword -a schema_module schema_name  
 
'''
    parser = argparse.ArgumentParser(description='Write kafka topic to stdin', epilog=example_usage, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--kafka-server', type=str, help='kafka server address', required=True)
    parser.add_argument('-t', '--topic', type=str, help='The kafka topic to observe', required=True)
    parser.add_argument('-g', '--group-name', type=str, help='The kafka Group Name (Client id is 1)', required=True)
    parser.add_argument('-u', '--kafka-username', type=str, help='kafka username')
    parser.add_argument('-p', '--kafka-password', type=str, help='password for the kafka user')
    parser.add_argument('-a', '--avro', nargs=2, metavar=('MODULE', 'SCHEMA'), type=str, help='Set avro schema if message is an avro message')
    parser.add_argument('-l', '--message-list', action='store_true', help='message contains a list which item each should go in a separate row')
    parser.add_argument('-b', '--binary', action='store_true', help='binary output')
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
            # With authentication through security credentials
            with KafkaConsumerContextManager(args.topic, group_id=args.group_name,
                                            bootstrap_servers=args.kafka_server, client_id=1,
                                            security_protocol='SASL_PLAINTEXT',
                                            sasl_mechanism='PLAIN', 
                                            sasl_plain_username=args.kafka_username,
                                            sasl_plain_password=args.kafka_password,
                                            enable_auto_commit=False) as consumer:
                parse_messages(consumer,args)
        else:
            # Without authentication
            with KafkaConsumerContextManager(args.topic, group_id=args.group_name,
                                            bootstrap_servers=args.kafka_server, client_id=1,
                                            enable_auto_commit=False) as consumer:
                parse_messages(consumer,args)     
    except KeyboardInterrupt:
        logging.error('stopping due to keyboard interrupt')


def parse_messages(consumer,args):
    """
    Parses the Kafka-Message and writes it into stdout
    """
    systemd_notifier = sdnotify.SystemdNotifier()
    systemd_notifier.notify('READY=1')

    if args.avro:
        # Load Avro Schema
        config_schema = __import__(args.avro[0], fromlist=[args.avro[1]])
        schema = getattr(config_schema, args.avro[1])
        messages = consumer.avro_messages(schema, batched=True)
    else:
        messages = consumer.consumer

    for message in messages:
        # Parse messages
        systemd_notifier.notify('WATCHDOG=1')
        logging.debug(f'received message')

        if args.avro:
            # avro is batched
            for m in message:
                write_message(json.dumps(m)+"\n", args.binary)
        else: 
            if not args.message_list:
                # One entry per message
                write_message(message,args.binary)
            else:
                # Multiple entries per kafka message -> parse entries
                # List without avro: expecting JSON
                decode_json_list(message, args)
            consumer.consumer.commit()


def decode_json_list(message, args):
    """
    Decodes a JSON list and writes it to stdout
    """
    message_list = json.loads(message.value.decode('utf-8'))
    if not isinstance(message_list, list):
        logging.fatal('message is not a list. Cannot split it into lines')
        return
    if not message_list:
        logging.fatal('empty message list')
        return
    for row in message_list:
        to_write = json.dumps(row) + "\n"
        write_message(to_write, args.binary)


def write_message(message, binary):
    """
    Writes given message to stdout
    """
    if binary: 
        sys.stdout.buffer.write(message.value)
        sys.stdout.buffer.write(b'\n')
    else:
        sys.stdout.write(message.value.decode('utf-8')+"\n")
    sys.stdout.flush()


if __name__ == '__main__':
    main()

