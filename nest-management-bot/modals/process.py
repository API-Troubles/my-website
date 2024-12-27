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
                    "text": f"*MEM Used (RSS):* {process_info['memory']['rss'] / 1024**3:.2f} GB" # convert to GB
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
                            "text": "Kill the process :kirby_gun: (SIGTERM)",
                            "emoji": True
                        },
                        "value": f"{process_info['pid']}-e-sigterm",
                        "action_id": "kill-process-1" # die process, die! (SIGTERM)
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Brutal Death (SIGKILL)",
                            "emoji": True
                        },
                        "value": f"{process_info['pid']}-e-sigkill",
                        "action_id": "kill-process-2" # die process, die! but not nicely (SIGKILL)
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Use SIGTERM when possible. SIGTERM allows the process to gracefully shut down (or sometimes completely ignore it). SIGKILL is absolutely brutal, the process straight up dies. That leaves no chance for data saving and stuff so use only when needed._"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Resume the Process" if process_info['status'] == "stopped" else "Pause the Process",
                            "emoji": True
                        },
                        "value": f"{process_info['pid']}",
                        "action_id": "resume-process" if process_info['status'] == "stopped" else "pause-process"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Please remember to unpause it :im-sobbing:_"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Be careful, messing with processes can indeed cause problems, watch wat you wish for.{" This process is also critical to the running of this bot, touching it *will* break something. Be careful... I'm not stopping you tho." if not process_info['safe_kill'] else ''}_"
                }
            }
        ]
    }


def process_kill_success_modal(process_pid):
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
                    "text": f"You did it, you killed a process (`PID: {process_pid}`). Be proud of yourself I guess? Lay low and hope you aren't caught by the cops tho..."
                }
            }
        ]
    }


def process_action_success_modal(action, process_pid):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Success :yay:",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Thanks :)",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"You did it, you {action}ed a process (`PID: {process_pid}`). Get back to what you're doing now :D"
                }
            }
        ]
    }