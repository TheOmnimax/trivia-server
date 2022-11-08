# Trivia server

This is the server for the [Max Trivia](https://github.com/TheOmnimax/max-trivia) app.

## About

This server is used for both management and playing.

For management, it uses Flask to create a REST API. That REST API can be used to create new questions and categories that can then be used in the game.

For playing, WebSockets are used through Socket.io to connect to clients and communicate in order to play the game.

## Documentation files

Documentation files can be found in [this folder](https://github.com/TheOmnimax/trivia-server/tree/main/docs).