import argparse
import logging

import kafka.errors
import kafkahelper


def main():
    parser = argparse.ArgumentParser(description='Parse bgpstream.com and publish new alerts to redis')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='enable debug logging. -vv enables also kafka debug logging')
    parser.add_argument('-t', '--topic', type=str, help='The kafka topic to observe')
    parser.add_argument('-g', '--group-name', type=str, help='The kafka Group Name (Client id is 1 by default')
    parser.add_argument('-o', '--output-dir', type=str, help='The output directory')
    parser.add_argument('-a', '--avro', action='store_true', help='message is an avro message')
    parser.add_argument('-l', '--message-list', action='store_true', help='message contains a list which item each '
                                                                          'should go in a separate row')
    parser.add_argument('--kafka-server', type=str, help='The server address of the kafka broker')
    parser.add_argument('--kafka-username', type=str, help='The username for the kafka broker')
    parser.add_argument('--kafka-password', type=str, help='The password for the kafka broker')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose > 0 else logging.INFO,
                        format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

    if args.verbose == 1:
        for name in logging.root.manager.loggerDict:
            if name.startswith('kafka.'):
                kafka_logger = logging.getLogger(name)
                kafka_logger.setLevel(logging.INFO)

    try:
        with kafkahelper.KafkaConsumerContextManager(args.topic, group_id=args.group_name,
                                                     bootstrap_servers=args.kafka_server, client_id='0',
                                                     security_protocol='SASL_PLAINTEXT',
                                                     sasl_mechanism='PLAIN', sasl_plain_username=args.kafka_username,
                                                     sasl_plain_password=args.kafka_password,
                                                     enable_auto_commit=False) as consumer:
            messages = consumer.avro_messages(kafkahelper.bgp_bill_schemas.BASICALERTSCHEMA) if args.avro else consumer.consumer
            for message in messages:
                # Depending on the type of your topic the messge will be an bytes array or an object
                ############################################################################################
                # Do something with the message HERE
                ############################################################################################
                consumer.consumer.commit()
    except KeyboardInterrupt:
        logging.error('stopping due to keyboard interrupt')
    finally:
        pass


def simple_producer_example(args):
    with kafkahelper.KafkaProducerContextManager(bootstrap_servers=[args.kafka_server],
                                                 compression_type='lz4', security_protocol='SASL_PLAINTEXT',
                                                 sasl_mechanism='PLAIN', sasl_plain_username=args.username,
                                                 sasl_plain_password=args.kafka_password) as producer:
        try:
            producer.write_avro({'example': 'with avro'}, BASICALERTSCHEMA, args.topic)  # ATTENTION SCHEMA in example is not correct
        except kafka.errors.KafkaError:
            logging.exception('Kafka Exception')

        producer.write('text example \n', args.topic)


if __name__ == '__main__':
    main()

