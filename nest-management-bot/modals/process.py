status_emojis = {
    "running": "🏃",
    "sleeping": "😴",
    "zombie": "🧟",
    "stopped": "⏹️",
    "disk-sleep": "💽"
}

def process_info_modal(process_info):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Process Management",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Ok bye bye",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Basic Info:* `{process_info['name']}` - PID: {process_info['pid']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*CPU Usage:* {process_info['cpu_usage']}% (100% is full usage on _1_ core)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*CPU Time:* {process_info['cpu_time']['user']} seconds"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*MEM Used (RSS):* {process_info['memory']['rss'] / 1024**3:.2f}/2.00 GB" # convert to GB
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Status:* {process_info['status']} ({status_emojis.get(process_info['status'], '')})"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Kill the process :kirby_gun:",
                            "emoji": True
                        },
                        "value": f"{process_info['pid']}",
                        "action_id": "kill-process" # die process, die! (nicely, its SIGTERM not SIGKILL lol)
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Be careful, killing processes can indeed cause problems, watch wat you wish for.{" This process is also critical to the running of this bot, killing *will* likely break something. Be careful... I'm not stopping you tho." if not process_info['safe_kill'] else ''}_"
                }
            }
        ]
    }

def process_kill_success_modal(process_info):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Success :yay:",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Okie tysm",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You did it, you killed a process (`PID: `{process_info['pid']}`). Be proud of yourself I guess? Lay low and hope you aren't caught by the cops tho..."
                }
            }
        ]
    }