# Nest Management Bot
Websocket Docs

wip docs, all items inside are subject to change. Some doc items are for what's planned and haven't been fully implemented yet


## Websocket Docs
### Message Syntax
All messages have a status, along with a message or payload:
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

The following are valid status types:
- `info`
- `command`
- `command_response`
- `command_response_error`
- `warning`
- `error`

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
- `obtain_all_process_info` (no payload)
- `obtain_process_info`(payload of `pid`)
- `kill_process`(payload of `pid`)
- `start_service` (payload of `service_name`)
- `stop_service` (payload of `service_name`)
- `restart_service` (payload of `service_name`)
- `reload_service` (payload of `service_name`)
- `exec_command` (payload of `command`)

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