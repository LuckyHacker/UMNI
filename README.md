# UMNI
Universal Multiplayer Network Interface

This project is made to provide multiplayer capabilities for games developed with <a href="http://game-editor.com">Game Editor</a>.

## Usage

### Client:
Client uses 4 files: config.json, local.data, remote.data and config.data (creates these files automatically). Client will use server provided tickrate and client ID. Client also starts up your game, and runs in the background. When game is shut down, client will also shutdown. local.data and remote.data files will be read/updated TICKRATE times per second. 

#### config.json:
In this config file you can specify game path and host address (server address).

#### local.data:
Write your game data in here, which you want to send to other clients.

#### remote.data:
Clients' local.data files and timestamp will be combined in this file as simple as this: timestamp + newline + local.data1 + local.data2 + local.data3 etc. So every client's local.data file will be in everyone's remote.data file.

#### config.data:
Server provided client ID will be in this file. You want to read this file as soon as game starts.

### Server:
Server uses only 1 file: config.json (creates file automatically). In this file you can specify host address and tickrate.
