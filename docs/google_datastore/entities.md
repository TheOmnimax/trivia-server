# Google Datastore - Entities

## game_room

**id**: ID of the game room.

**host_id** [str]: Player ID of the host

**members** [List[str]]: Player IDs who are a member of this game room.

**game** [str]: ID of the game being played

**last_change**: Last time the game has been changed or updated. This is used for cleanup.

## game

**id**: ID of the game

**type**: Type of game being played (e.g. "MaxTrivia")

**players**: IDs of players in the game.

There will also be several properties exclusive to certain game types.

## player

**id**: Player ID

**name**: Name of the player

**time_used**: Time taken up by the player so far this round

**score**: Player score so far