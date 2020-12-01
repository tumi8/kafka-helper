#!/usr/bin/env python

from distutils.core import setup

install_requires = ['kafka-python>=2.0.0', 'fastavro>=1.2.0']

setup(name='I8 Kafka Helper',
      version='0.1',
      description='A kafka helper with some schemas used at I8',
      author='TUM I8',
      author_email='sattler@net.in.tum.de',
      url='https://gitlab.lrz.de/netintum/projects/gino/tools/kafka-helper',
      packages=['kafkahelper'],
      install_requires=install_requires,
     )

