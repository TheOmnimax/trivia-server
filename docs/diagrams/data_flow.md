# Sequence diagrams

## Game creation

```mermaid
sequenceDiagram
autonumber
  App->>Server: Create game room: host_name
  activate Server
  Server-->>App: Game room created: room_code, host_id
  deactivate Server
  App->>Server: Create game: room_code, host_id, categories, num_rounds (opt)
  activate Server
  Server-->>App: Game created: successful
  deactivate Server
```
Note: When the app is told that the game room has been created, it will automatically then request the game itself being created, without any prompting from the user.

## Join game

```mermaid
sequenceDiagram
autonumber
  App->>Server: Join game: room_code
  activate Server
  Server-->>App: Add player to room: player_id
  Server-->>App: List of players sent to users: player_names
  deactivate Server
```

## Playing game

```mermaid
sequenceDiagram
autonumber
  App->>Server: Game is started by host.
  Server-->>App: Question data sent to players.
  App->>Server: Answer question
  Server-->>App: Send next question when next round is ready
```

