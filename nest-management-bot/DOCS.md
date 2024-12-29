# Nest Management Bot
wip docs, all items inside are subject to change. Some doc items are for what's planned and haven't been fully implemented yet
for questions and to contribute, DM @Felix Gao on Hack Club's slack :D

## Websocket Docs
### Message Syntax
All messages have a status, along with a message or payload. Usually messages aren't read by the code, but often used to hide funny easter eggs and to transmit certain messages for the user to see.
```json
{
  "status": "info",
  "message": "example message to send"
}
```
or...
```json
{
  "status": "command_response",
  "payload": {
    "data": [1, 2, 3, 4, 5]
  }
}
```
Payloads can either be a dictionary (`{'key': 'value'}`) or a list (`[1, 2, 3, 4, 5]`) depending on its usage.


The following are valid status types:
- `info` (these are usually messages which will be logged)
- `command`
- `command_response`
- `command_response_error`
- `warning` (unused for now)
- `error` (errors which aren't command responses, basically only sent by the server)

Command responses and commands can also include a payload item with anything inside:
```json
{
  "status": "command_response",
  "message": "response_download_raid_shadow_legends",
  "payload": {
    "example_data": "pls i downloaded, let my family go :sob:"
  }
}
```

Errors suck :(
```json
{
  "status": "command_response_error",
  "message": "response_download_raid_shadow_legends",
  "payload": {
    "error": "I like NordVPN better l bozo take that mister server!"
  }
}
```

Commands may have a payload in cases where more specific info is needed
```json
{
  "status": "command",
  "message": "obtain_process_info",
  "payload": {
    "pid": 43235
  }
}
```

Commands can have the following message text:
- `obtain_user_usages` (no payload)
- `obtain_all_process_info` (no payload)
- `obtain_process_info`(payload of `pid`)
- `kill_process`(payload of `pid` and `method` [`SIGKILL` or `SIGTERM`])
- `pause_process`(payload of `pid`)
- `resume_process`(payload of `pid`)
- `list_services` (no payload)
- `obtain_service_info` (payload of `service_name`)
- `start_service` (payload of `service_name`)
- `stop_service` (payload of `service_name`)
- `restart_service` (payload of `service_name`)
- `reload_service` (payload of `service_name`)

### Connecting:
To connect fully, the client needs to send the following message (with a different `client_token`)
```json
{
  "status": "let_me_in_pls",
  "message": "let me in! :D",
  "payload": {
    "version": "0.1.0a",
    "client_token": "e70f344347c59f6619489ee2b11c453dc9c25b2e33ddc532c73ebbc0b2b4684f.ddc69770"
  }
}
```

The server will verify the data sent and then either disconnect the client if the data is incorrect, or keep the connection and send back the following:
```json
{
  "status": "info",
  "message": "Authenticated :D"
}
```
Once that message is received, the client is fully connected. The server will log the client as connected and the user can interface with the bot, sending it commands through the websocket.

# Database Docs

This bot makes use of PostgreSQL to store data and settings for users. This documentation covers what is stored basically.

## Tables (Not case sensitive)
### `Users`
With columns:
- `token` text, a token used to connect to the websocket (see websocket docs)
- `slack_id` varchar(73), the user's slack ID

The token's generation code can be found in `client_utils.py` somewhere

### `Settings`
With columns:
- `slack_id`: varchar(73), the user's slack ID (linked to `users.slack_id`)
- `setting`: varchar(256), the setting name (see below for valid values)
- `setting_value`: varchar(256), the setting value

Valid settings and their values:

*marks the default value
- `storage_unit_of_measurement`: Either `bytes`, `gb`*, or `gib`
- `mem_or_ram`: Either `mem`* or `ram` (`mem` is ofc better)
- `tutorial`: A number between `stage_1` and `stage_3` (solely used internally to measure user tutorial progress, `stage_3` is done)