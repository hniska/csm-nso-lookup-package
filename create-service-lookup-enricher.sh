curl -k -X "POST" "https://localhost/graze/v1/createWorkflow" \
    -H 'Content-Type: application/json' \
    -u 'graze:graze' \
    -d $'{
        "active": true,
        "description": "NSO Service Lookup Enricher",
        "first_match_only": false,
        "id": 5,
        "moolet_name": "Enrichment Workflows",
        "operations": [
            {
                "duration": 0,
                "reset": false,
                "type": "delay"
            },
            {
                "forwarding_behavior": "always forward",
                "function_args": {
                    "field": "custom_info.eventDetails.nso",
                    "key": "source",
                    "lifespan": 30,
                    "lookupName": "device-to-service"
                },
                "function_name": "staticLookup",
                "operation_name": "ServiceLookup",
                "type": "action"
            }
        ],
        "sequence": 2,
        "sweep_up_filter": {},
        "workflow_name": "NSO Service Lookup"
    }'
