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

__all__ = ['BASICALERTSCHEMA', 'TLSTARGETSCHEMA', 'IRRSCHEMA']

