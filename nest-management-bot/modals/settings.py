def settings_modal():
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Service Action",
            "emoji": true
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
                    "text": "_Note: Whatever option is bolded is what you have selected currently._"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*MEM* / RAM"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select MEM pls",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*MEM*",
                                "emoji": True
                            },
                            "value": "mem"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*RAM*",
                                "emoji": True
                            },
                            "value": "ram"
                        },
                    ],
                    "action_id": "settings-mem-vs-ram"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Unit of Measurement (Data)"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a Unit",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*GB*",
                                "emoji": True
                            },
                            "value": "gb"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*GiB*",
                                "emoji": True
                            },
                            "value": "gib"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*Bytes*",
                                "emoji": True
                            },
                            "value": "bytes"
                        }
                    ],
                    "action_id": "settings-unit-data"
                }
            }
        ]
    }