# UMNI
Universal Multiplayer Network Interface

This project is made to provide multiplayer capabilities for games developed with <a href="http://game-editor.com">Game Editor</a>.

## Usage
### Client:
Client uses 4 files: config.json, local.data, remote.data and config.data.
".data" files are for your game and config.json is config file for client. In this config file you can specify game path and host address (server address).
#### local.data
Write your game data in here, which you want to send to other clients.
#### remote.data
Clients' local.data files will be combined in this file as simple as this: local.data1 + local.data2 + local.data3 etc.
#### config.data
Server provided player ID will be in this file. You want to read this file as soon as game starts.
### Server:
Server uses only 1 file: config.json. In this file you can specify host address and tickrate.
