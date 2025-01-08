def settings_modal(settings_info):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Settings",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Byee!",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Settings... wow! I don't know what much else to say. Umm... get button pressing and customizing!! NOW!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Note: Whatever option is in gray in the selection box is what you have selected currently._"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "MEM / RAM"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": settings_info['mem_vs_ram'],
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "MEM",
                                "emoji": True
                            },
                            "value": "MEM"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "RAM",
                                "emoji": True
                            },
                            "value": "RAM"
                        },
                    ],
                    "action_id": "settings-mem-vs-ram"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Unit of Measurement (Storage)"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": settings_info['storage_unit_of_measurement'],
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "GB",
                                "emoji": True
                            },
                            "value": "GB"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "GiB",
                                "emoji": True
                            },
                            "value": "GiB"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Bytes",
                                "emoji": True
                            },
                            "value": "Bytes"
                        }
                    ],
                    "action_id": "settings-unit-data"
                }
            }
        ]
    }