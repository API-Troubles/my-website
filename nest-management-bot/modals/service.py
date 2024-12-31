def service_info_modal(service_info):
    base = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Service Management",
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
                    "text": f"*Service Name:* {service_info['name']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:* \"{service_info['description']}\""
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*File Location:* _{service_info['file_location']}_"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*State:* {service_info['active_state']} ({service_info['sub_state']})"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Up Since:* {service_info['uptime']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Main PID:* {service_info['pid']}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Manage Process",
                        "emoji": True
                    },
                    "value": f"{service_info['pid']}-update",
                    "action_id": "manage-process"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Uptime information may differ by a few seconds when compared to systemctl. Why? I have literally no clue, feel free to check out my jank code though!_"
                }
            }
        ]
    }
    if service_info['active_state'] in ["inactive", "failed"]:
        base["blocks"].insert(-1, {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Start Service",
                        "emoji": True
                    },
                    "value": f"{service_info['name']}-start",
                    "action_id": "manage-service-action-1"
                }
            ]
        })
    else:
        base["blocks"].insert(-1, {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Stop Service",
                        "emoji": True
                    },
                    "value": f"{service_info['name']}-stop",
                    "action_id": "manage-service-action-1"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Restart Service",
                        "emoji": True
                    },
                    "value": f"{service_info['name']}-restart",
                    "action_id": f"manage-service-action-2"
                }
            ]
        })
        base["blocks"].insert(-1, {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reload Service",
                        "emoji": True
                    },
                    "value": f"{service_info['name']}-reload",
                    "action_id": "manage-service-action-3"
                }
            ]
        })
    if service_info['name'] == "nest-management-bot.service": # Hope this warning works, prob not but oh well :pf:
        base["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "_Woah there! This service is quite literally the service that makes this bot function. Watch what you do but I'm not stopping you ¯\\_(ツ)_/¯._"
            }
        })

    return base


def service_action_modal(service_name, action):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Service Action",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Thanks :D",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You have _{action}ed_ `{service_name}` :yay:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Now get back to whatever you're meant to do :).",
                    "emoji": True
                }
            }
        ]
    }