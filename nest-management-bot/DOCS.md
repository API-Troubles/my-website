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
- `obtain_global_info`
- `obtain_all_process_info`
- `obtain_process_info`
- `kill_process`
- `restart_process`*
- `start_process`*
- `exec_command`

*Makes use of systemd (tbd)

### Connecting:
To connect fully, the client needs to send the following message
```json
{
  "status": "let_me_in_pls",
  "message": "let me in! :D",
  "payload": {
    "version": "0.1.0a"
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