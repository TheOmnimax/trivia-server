# Google Datastore - Entities

Data is stored as Google Datastore entities. Every entity will have a **name/ID**, which is its unique identifier. They will also have many other properties.

Many entities have a property called **type**. This is used by the server to determine which data class should be used.

These are the entities used (click on them to learn more):

[category](#category)
[game_room](#game_room)
[player](#player)
[question](#question)
[trivia_game](#trivia_game)

## category

**children** (List[str]): IDs of categories that are sub-categories of this category. For example, "Pokémon" is a sub-category of "Video games"

**label** (str): Friendly, user-facing name of the category.

**parents** (List[str]) (deprecated, do not use): IDs of categories that this category is the subcategory of.

## game_room

**game_id** (str): ID of the game currently being played in that game room (only one game can be played at a time in each game room).

**host_id** (str): Player ID of the host.

**members** (List[str]): Player IDs who are a member of this game room. They will become players in the game.

**type**

## question

Questions are stored using Datastore. They use the *kind* **question**. They use these properties:

**categories** (List[str]): List of categories this question is a part of (ties it to the [category](#category) entities).

**choices** (List[str]): List of choices that will be shown to the players.

**correct** (int): Index (starting at 0) of which choice is correct. For example, in **choices**, if the second choice is the correct choice, then this will have a value of 1.

**label** (str): Question to be asked.

**shuffle** (bool): Whether the choices should be shuffled. (Currently not implemented.)

**shuffle_skip** (List[int]): The indexes of which choices should not be shuffled. (Currently not implemented.)

## trivia_game

**categories**: Which categories the retrieved questions for the game should be a part of.

**complete_players** (List[str]): IDs of players who have so far completed the round. Gets reset at the end of each round.

**final_scores** (Optional[Dict[str, int]]): Key is player IDs, and value is their score at the end of the game.

**game_complete** (bool): Whether all of the questions have been shown and completed.

**game_winners** (Optional[List[str]]): IDs of players who got the highest score.

**num_rounds** (int): How many questions should be shown during the game.

**players**: (List[str]): IDs of players in the game.

**question_index** (int): Index of which question the game is on. Starts at -1 when the game hasn't started, then increases to 0 for the first question, 1 for the second, and so on. When it equals **num_rounds**, the game is over.

**questions** (List[Dict]): Questions that will be shown during the game. Saved here instead of retrieving the entity to save time. In each dict, there will be two keys: "choices" is the list of choices, and "label" is the question to be asked.

**round_complete** (bool): Whether the round is complete. Starts as `False`, becomes `True`, then back to `False` when onto the next round.

**round_winners** (List[Optional[str]]): ID of who won each round. Can be blank if a round had no winner. First ID is winner of first round, second ID is winner of second round, etc.

**scores** (Dict[str, int]): Scores of players so far. (Not yet implemented.)

## trivia_player

**completed_round** (bool): Whether the player has answered the question yet.

**name** (str): Name of the player.

**ready** (bool): Whether player is ready for the next round. (Currently not used.)

**score** (int): Player score so far. (Currently not used.)

**selected_choice** (int): Index of the choice they selected for the question. Has value of -1 if they have not selected a choice yet.

**socket** (str): ID of the socket used, so easy to communicate with them using Socket.io.