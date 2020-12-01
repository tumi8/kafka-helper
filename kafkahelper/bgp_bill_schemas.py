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

__all__ = ['BASICALERTSCHEMA', 'TLSTARGETSCHEMA']

