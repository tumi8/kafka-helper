import fastavro

BASICALERTSCHEMA = fastavro.parse_schema({
    'name': 'basic_alert',
    'namespace': 'heap',
    'type': 'record',
    'fields': [
        {
            'name': 'id',
            'type': 'string',
            'default': ''
        },
        {
            'name': 'subprefix',
            'type': 'string'
        },
        {
            'name': 'prefix',
            'type': 'string'
        },
        {
            'name': 'subprefix_origin',
            'type': {
                'type': 'array',
                'items': 'int'
            }
        },
        {
            'name': 'prefix_origin',
            'type': {
                'type': 'array',
                'items': 'int'
            }
        },
        {
            'name': 'start_time',
            'type': 'int'
        },
        {
            'name': 'detected_time',
            'type': 'int'
        },
        {
            'name': 'event_source',
            'type': 'int'
        },
        {
            'name': 'path',
            'type': {
                'type': 'array',
                'items': 'string'
            }
        },
        {
            'name': 'active_parent_origins',
            'type': {
                'type': 'array',
                'items': {
                    'name': 'parent_origins',
                    'namespace': 'heap',
                    'type': 'record',
                    'fields': [
                        {
                            'name': 'parent',
                            'type': 'string'
                        },
                        {
                            'name': 'origins',
                            'type': {
                                'type': 'array',
                                'items': 'int'
                            }
                        },
                        {
                            'name': 'last_announcements',
                            'type': {
                                'type': 'array',
                                'items': 'int'
                            },
                            'default': []
                        }
                    ]
                },
            },
            'default': []
        }
    ],
})

TLSTARGETSCHEMA = fastavro.parse_schema({
    'name': 'tls_target',
    'namespace': 'heap',
    'type': 'record',
    'fields': [
        {'name': 'ip', 'type': 'string'},
        {'name': 'server_name', 'type': 'string'},
        {'name': 'blocked', 'type': 'boolean'}
    ],
})

TLSIMPACTTARGETSCHEMA = fastavro.parse_schema({
    'name': 'tls_impact_targer',
    'namespace': 'heap',
    'type': 'record',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'ip', 'type': 'string'},
        {'name': 'server_name', 'type': 'string'},
        {'name': 'blocked', 'type': 'boolean'},
        {'name': 'scan_timestamp', 'type': 'int'},
        {'name': 'protocol', 'type': 'int'},
        {'name': 'cipher', 'type': 'string'},
        {'name': 'pub_key_hash', 'type': 'string'},
        {'name': 'cert_hash', 'type': 'string'},
        {'name': 'cert_valid', 'type': 'boolean'}
    ],
})

EVENTENDEDSCHEMA = fastavro.parse_schema({
    'name': 'event_end',
    'namespace': 'heap',
    'type': 'record',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {
            'name': 'end_reason',
            'type': {
                'name': 'end_reason',
                'type': 'enum',
                'namespace': 'heap',
                'symbols': ['MOAS', 'subMOAS', 'isLeastSpecific', 'withdrawed', 'notAnnounced', 'notAnnouncedByOrigin']
            }
        },
        {'name': 'withdrawal_ts', 'type': ['null', 'int'], 'default': None},
        {
            'name': 'moas_announcements',
            'type': ['null', {
                'type': 'array',
                'items': {
                    'name': 'moas_announcement',
                    'namespace': 'heap',
                    'type': 'record',
                    'fields': [
                        {'name': 'origin', 'type': 'int'},
                        {'name': 'announcement', 'type': 'int'},
                    ]
                }
            }],
            'default': None
        },
        {
            'name': 'submoas_announcements',
            'type': ['null', {
                'type': 'array',
                'items': {
                    'name': 'submoa_announcement',
                    'namespace': 'heap',
                    'type': 'record',
                    'fields': [
                        {'name': 'prefix', 'type': 'string'},
                        {'name': 'origin', 'type': 'int'},
                        {'name': 'announcement', 'type': 'int'},
                    ]
                }
            }],
            'default': None
        },
    ],
})

IRRSCHEMA = fastavro.parse_schema({
  "name": "irrrov",
  "type": "record",
  "namespace": "heap",
  "fields": [
    {
      "name": "id",
      "type": "string"
    },
    {
      "name": "rpki",
      "type": "int"
    },
    {
        "name": "prefix",
        "namespace": "heap",
        "type": {
            "type": "record",
            "name": "prefix",
            "namespace": "heap",
            "fields": [
                {"name": "irr", "type": "boolean"},
                {"name": "crank",
                 "type": ["null", {
                     "name": "crank",
                     "type": "record",
                     "fields": [
                         {"name": "rank", "type": ["null", "int"]},
                         {"name": "seen", "type": ["null", "boolean"]},
                         {"name": "clique", "type": ["null", "boolean"]},
                         {"name": "cc", "type": ["null", "string"]},
                         {"name": "cone",
                          "type": {
                              "name": "cone",
                              "type": "record",
                              "fields": [
                                  {"name": "numberAsns", "type": ["null", "int"]},
                                  {"name": "numberPrefixes", "type": ["null", "int"]},
                                  {"name": "numberAddresses", "type": ["null", "long"]}
                              ]
                          }
                          },
                         {"name": "asnDegree",
                          "type": {
                              "name": "asnDegree",
                              "type": "record",
                              "fields": [
                                  {"name": "provider", "type": ["null", "int"]},
                                  {"name": "peer", "type": ["null", "int"]},
                                  {"name": "customer", "type": ["null", "int"]},
                                  {"name": "total", "type": ["null", "int"]},
                                  {"name": "transit", "type": ["null", "int"]},
                                  {"name": "sibling", "type": ["null", "int"]}
                              ]
                          }
                          },
                         {"name": "announcing",
                          "type": {
                              "name": "announcing",
                              "type": "record",
                              "fields": [
                                  {"name": "numberPrefixes", "type": ["null", "int"]},
                                  {"name": "numberAddresses","type": ["null", "int"]}
                              ]
                          }
                          }
                     ]
                 }]
                 },
                {"name": "aspop",
                 "type":  ["null", {
                     "name": "aspop",
                     "type": "record",
                     "fields": [
                         {"name": "rank", "type": ["null", "int"]},
                         {"name": "cc", "type": ["null", "string"]},
                         {"name": "users", "type": ["null", "int"]},
                         {"name": "samples", "type": ["null", "int"]}
                     ]
                 }]
                 },
                {"name": "cclass",
                 "type":  ["null", {
                     "name": "cclass",
                     "type": "record",
                     "fields": [
                         {"name": "type", "type": ["null", "int"]},
                         {"name": "reason", "type": ["null", "int"]}
                     ]
                 }]
                 }
            ]
        }
    },
    {
      "name": "subprefix",
      "type": "prefix"
    }
  ]
})


__all__ = ['BASICALERTSCHEMA', 'TLSTARGETSCHEMA', 'IRRSCHEMA', 'TLSIMPACTTARGETSCHEMA', 'EVENTENDEDSCHEMA']

