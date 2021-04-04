# API Reference

This is the documentation for the whole library.

## Version Related Info :id=version

`dogehouse.__version__`  
A string representation of the version which follows the [Semantic Version 2.0.0 Guidelines](https://semver.org/). For example `1.0.0`.

## Listeners

There are currently two listeners in the library, the event listener and the command listener.

### Events :id=event-listener

The events get registered by the `dogehouse.event` decorator. All events that are recognised can be found in the [Event Reference](api?id=events)

##### Example

```py
import dogehouse

class Client(dogehouse.DogeClient):
    @dogehouse.event
    async def on_ready(self):
        print(f"Logged in as {self.user.username}")

if __name__ == "__main__":
    Client("token", "refresh_token").run()
```

The `Logged in as <your client username>` will be printed when the client has connected successfully.

### Commands :id=command-listener

?> All commands **MUST** be a [coroutine](https://docs.python.org/3/library/asyncio-task.html#coroutine). If you want to throw away all supplied arguments that aren't used you **MUST** supply a context parameter. *(Which can be an `_` if you don't plan to use it)*

!> [CommandAlreadyDefined](api?exceptions-commandalreadydefined) exception?  
    This exception gets raised when that command name has already been defined in a command name or as a command alias.

Create a new DogeClient command, which will be handled by the dogehouse python library.

> **Note:** All commands are automatically case insensitive.

##### Arguments

* `func` *(Awaitable, optional)*: Your function (gets supplied automatically when you use the decorator). Defaults to None.
* `name` *(str, optional)*: The call name for your command. Defaults to the function name.
* `cooldown` *(int, optional)*: The cooldown for the function usage per client. Defaults to 0.
* `aliases` *(List of strings, optional)*: A list of aliases which should trigger your command. Defaults to None.

##### Example

```py
import dogehouse

class Client(dogehouse.DogeClient):
    @dogehouse.command
    async def hello(self, ctx):
        await self.send(f"Hello {ctx.author.mention}")

    @dogehouse.command(name="foo", aliases=["bar", "foobar"])
    async def foobar_command(self, _):
        await self.send(f"Foo bar's")
    
if __name__ == "__main__":
    Client("token", "refresh_token").run()
```

> **Note:** In your script the bot will have to join/create a room first.

This will register a command `hello` that calls `hello()`. So when a user types `!hello` the client will respond with `Hello @<username>`.

The second command is a bit more complex, for this command `foobar_command` will **NOT** be the command call. As it is overriden by the `name` parameter in the decorator. So this command will get triggered when a user types `!foo`. And all the aliases we created get recognised as a seperate command, but using the same command call. So `!foo`, `!bar` and `!foobar` all call the `foobar_command()` coroutine.


## Event Reference :id=events

?> **HELP** my event is not getting triggered!
    Don't worry, you probably did something wrong, so lets resolve that.  
    Check the following list, if it still doesn't work, feel free to create a [Github Issue](https://github.com/Arthurdw/dogehouse.py/issues).  
    &nbsp;  <!-- Big brain action to implement an empty line -->  
    - All events **MUST** be a [coroutine](https://docs.python.org/3/library/asyncio-task.html#coroutine). If they aren't you might get unexpected errors. To turn a function into a coroutine, let the function start with `async def` instead of `def`.  
    - All events **MUST** contain all parameters in the function. If you don't plan on using a certain parameter, just place a `_` instead of a proper argument name.

### `on_ready`

This event gets called when the client has started the heartbeat, listeners and has received that the `token` and `refresh_token` are valid from [dogehouse.tv](https://dogehouse.tv).

### `on_error`

This event gets called when an exception has occured.

##### Parameters

* `error` *(Exception)*: The exception that got thrown.

### `on_cooldown_trigger`

This event gets called when a user tried to execute a command, but it is still on cooldown for them.

##### Parameters

* `ctx` *([Context](api?id=entity-context))*: The context of the command instance.
* `command_name` *(string)*: The name of the command.
* `command` *(Awaitable)*: The command that should get executed, but was prevented because of the cooldown.
* `time_left` *(float)*: The amount of sec the user has to wait untill it can use the command again.

### `on_rooms_fetch`

This event gets called when the client has received all the new public rooms and has applied them to the [`DogeClient.rooms`](api?id=entity-dogeclient) property.

### `on_room_join`

This event gets called when the client joins a room.

##### Parameters

* `as_speaker` *(bool)*: Wether or not the client joined the room as a speaker or not.

### `on_room_users_fetch`

This event gets triggered when all the users from the current room have been fetched.

### `on_user_fetch`

This event gets called when a specific user has been fetched.

##### Parameters

* `user` *([User](api?id=entity-user))*: The user that has been fetched.

### `on_user_join`
### `on_user_leave`

These events get called when a user joins/leaves the current room.

##### Parameters

* `user` *([User](api?id=entity-user))*: The user that joined/left.

### `on_message`

This event gets called when a message has been sent in the chat.

##### Parameters

* `message` *([Message](api?id=entity-message))*: The message that got sent.

### `on_message_delete`

This event gets called when a message has been removed.

##### Parameters

* `deleter_id` *(string)*: The id of the user who deleted the message.
* `message_id` *(string)*: The id of the message that got deleted.

### `on_speaker_request`

This event gets called when a user has requested to speak in the room.

##### Parameters

* `user_id` *(string)*: The id of the user who requested to speak.
* `room_id` *(string)*: The id of the room in which the user requested to speak. 

### `on_speaker_add`

This event gets called when a speaker has been added.

##### Parameters

* `user_id` *(string)*: The id of the user who has been added to the speakers list.
* `room_id` *(string)*: The id of the room to which the user now can speak in.
* `muted` *(A dictionary with as keys strings and values booleans)*: A dictionary where the keys are the userid's from speakers and the value is wheter or not they are muted 

### `on_speaker_delete`

This event gets called when a speaker has been removed

##### Parameters

* `user_id` *(string)*: The id of the user who has been added to the speakers list.
* `room_id` *(string)*: The id of the room to which the user now can speak in.
* `muted` *(A dictionary with as keys strings and values booleans)*: A dictionary where the keys are the userid's from speakers and the value is wheter or not they are muted 
* `raised_hands` *(A dictionary with as keys strings and values booleans)*: A dictionary where the keys are the userid's from speakers and the value is wheter or not they have asked to speak.

### `on_user_ban`

The event that gets called when a user has been banned.

##### Parameters

* `user_id` *(string)*: The id of the user who has been banished.

## Entitities

!> All of these entitities should not be manually created by the client. These are inteded to be created by the [DogeClient](api?id=dogeclient)

### Client :id=entity-client

The base client. All these attributes are accessable using the [DogeClient](api?id=dogeclient).

##### Attributes

* `user` *([User](api?id=entity-user))*: The client its user object.
* `room` *([Room](api?id=entity-room))*: The current room in wich the Client resides. Is `None` if no room has been joined.
* `rooms` *(List of [Room](api?id=entity-room)s)*: A collection of all the rooms which the client has cached. This gets fetched automatically if no room has been joined. You can also update this using the `async DogeClient.get_top_public_rooms` method.
* `prefix` *(List of strings)*: A collection of prefixes to which the client should respond.

<!-- dogehouse.DogeClient -->
### DogeClient([Client](api?id=entity-client)) :id=dogeclient

Represents your Dogehouse client.

##### Arguments

* `token` *(string)*: Your super secret client token.
* `refresh_token` *(string)*: Your super secret client refresh token.
* `room` *(integer, optional)*: The room your client should join. Defaults to None.
* `muted` *(bool, optional)*: Wether or not the client should be muted. Defaults to False.
* `reconnect_voice` *(bool, optional)*: When the client disconnects from the voice server, should it try to reconnect. Defaults to False.
* `prefix` *(List of strings or a string, optional)*: The bot prefix.
* `telemetry` *(telemetry object)*: The telemetry class that will be used. Defaults to None.

#### `async` run(): :id=dogeclient-run

Establishes a connection to the websocket servers, this also starts the client heartbeat & event loop.

#### `async` close(): :id=dogeclient-close

Closes the established connection.

##### Raises

* [`NoConnectionException`](api?id=exceptions-noconnectionexception): No connection has been established yet. Aka got nothing to close.

#### `async` get_top_public_rooms(*, cursor): :id=dogeclient-get_top_public_rooms

Manually send a request to update the client rooms property.
This method gets triggered every *`X` seconds. 

*`X`: Stated in `dogehouse.config.topPublicRoomsInterval`

##### Arguments

* `cursor` *(int, optional)*: The cursor for the fetch request. Defaults to 0.

#### `async` create_room(name, description, *, public): :id=dogeclient-create_room

Creates a room, when the room is created a request will be sent to join the room.
When the client joins the room the [`on_room_join`](api?id=on_room_join) event will be called.

##### Arguments

* `name` *(string)*: The name for room.
* `description` *(string)*: The description for the room.
* `public` *(bool, optional)*: Wether or not the room should be publicly visible. Defaults to True.

#### `async` join_room(id): :id=dogeclient-join_room

Send a request to join a room as a listener. When the client has joined the room the [`on_room_join`](api?id=on_room_join) event will be called.

##### Arguments

* `id` *(string)*: The ID of the room you want to join.

#### `async` send(message, *, whisper): :id=dogeclient-send

Send a message to the current room.

##### Arguments

* `message` *(string)*: The message that should be sent.
* `whisper` *(List of strings, optional)*: A collection of user id's who should only see the message. Defaults to [].

##### Raises

* [`NoConnectionException`](api?id=exceptions-noconnectionexception): Gets thrown when the client hasn't joined a room yet.

#### `async` ask_to_speak(): :id=dogeclient-ask_to_speak

Request in the current room to speak.

##### Raises

* [`NoConnectionException`](api?id=exceptions-noconnectionexception): Gets raised when no room has been joined yet.   

#### `async` make_mod(user): :id=dogeclient-make_mod

Make a user in the room moderator.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user which should be promoted to room moderator.

#### `async` unmod(user): :id=dogeclient-unmod

Remove a user their room moderator permissions.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user from which his permissions should be taken.

#### `async` make_admin(user): :id=dogeclient-make_admin

Make a user the room administrator/owner.
NOTE: This action is irreversable.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user which should be promoted to room admin.

#### `async` set_listener(user): :id=dogeclient-set_listener

Force a user to be a listener.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user which should become a Listener. Defaults to the client.

#### `async` ban_chat(user): :id=dogeclient-ban_chat

Ban a user from speaking in the room chat.
NOTE: This action can not be undone.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user from which their chat permissions should be taken.

#### `async` ban(user): :id=dogeclient-ban

Bans a user from a room.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user who should be banned.

#### `async` unban(user): :id=dogeclient-unban

Unban a banned user from the room.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user who should be unbanned.

#### `async` add_speaker(user): :id=dogeclient-add_speaker

Accept a speaker request from a user.

##### Arguments

* `user` *(Union[string, User, BaseUser, UserPreview])*: The user who will has to be accepted.

#### `async` delete_message(id, user_id): :id=dogeclient-delete_message

Deletes a message that has been sent by a user.

##### Arguments

* `id` *(string)*: The id of the message that should be removed.
* `user_id` *(string)*: The author of that message.

#### `async` wait_for(event, *, timeout, check, tick, fetch_arguments): :id=dogeclient-wait_for

Manually wait for an event.

##### Arguments

* `event` *(string)*: The `on_...` event that should be waited for. *(without the `on_` part)*
* `timeout` *(float, optional)*: How long the client will wait for a response.. Defaults to 60.0.
* `check` *(callable, optional)*: A check which will be checked for the reponse. Defaults to None.
* `tick` *(float, optional)*: The tickrate for the fetch check iteration. Defaults to 0.5.

##### Raises

* [`asyncio.TimeoutError`](https://docs.python.org/3.8/library/asyncio-exceptions.html#asyncio.TimeoutError): Gets thrown when the timeout has been reached.

##### Returns

* `Union[Any, Tuple[Any]]`: The parameter(s) of the event.

#### `async` fetch_user(argument): :id=dogeclient-fetch_user

Currently only calls the [`DogeClient.get_user`](api?id=dogeclient-get_user) method, will implement user fetching in the future tho.

#### get_user(argument): :id=dogeclient-get_user

Fetch a user from the current room.  
Filtering order:
    1. ID match
    2. username match
    3. displayname match

##### Arguments

* `argument` *(str)*: The user argument.

##### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): The requested member could not be found

##### Returns

* [`User`](api?id=entity-user): The user that matches the params.


<!-- dogehouse.entitites.BaseUser -->
### BaseUser :id=entity-baseuser

?> Implements:  
    `__str__` = username

Represents the most basic information of a fetched user.

##### Attributes

* `id` *(string)*: The user their id.
* `username` *(string)*: The username of the user. *(Their mention name)*
* `displayname` *(string)*: The display name of the user.
* `avatar_url` *(string)*: The user their avatar URL.

#### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=baseuser-convert

Convert an argument (id, username, displayname) into a [BaseUser](api?id=entity-baseuser) object.

##### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up. 

##### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

##### Returns

A fully functional [BaseUser](api?id=entity-baseuser) object.

<!-- dogehouse.entitites.User -->
### User([BaseUser](api?id=entity-baseuser)) :id=entity-user

?> Implements:  
    `__str__` = username

Represents a dogehouse.tv user.

##### Attributes

* `id` *(string)*: The user their id.
* `username` *(string)*: The username of the user. (Their mention name)
* `displayname` *(string)*: The displayname of the user.
* `avatar_url` *(string)*: The user their avatar URL.
* `bio` *(string)*: The user ther biography.
* `last_seen` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the user was last online.
* `online` *(bool)*: Whether or not the user is currently online
* `following` *(bool)*: Wheter or not the client is following this user.
* `room_permissions` *([Permission](app?id=entity-permission))*: The user their permissions for the current room.
* `num_followers` *(int)*: The amount of followers the user has.
* `num_following` *(int)*: The amount of users this user is following.
* `follows_me` *(bool)*: Wether or not the user follows the client.
* `current_room_id` *(string)*: The user their current room id.

#### to_base_user(): :id=user-to_base_user

Convert a user object to a [BaseUser](api?id=entity-baseuser) object.
This is intended for internal use (Convertors), as you can access all baseuser properties from the user object.

##### Returns

The newly created [BaseUser](api?id=entity-baseuser) object, which is derived from the current object.

#### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=user-convert

Convert an argument (id, username, displayname) into a [User](api?id=entity-user) object.

##### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up. 

##### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

##### Returns

A fully functional [User](api?id=entity-user) object.

<!-- dogehouse.entitites.UserPreview -->
### UserPreview :id=entity-userpreview

?> Implements:  
    `__str__` = displayname

Represents a userpreview from the [`Client.rooms`](api?id=entity-client) users list.

##### Attributes

* `id` *(string)*: The user their id.
* `displayname` *(string)*: The display name of the user.
* `num_followers` *(integer)*: The amount of followers the user has.

#### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=userpreview-convert

Convert an argument (id, username, displayname) into a [UserPreview](api?id=entity-userpreview) object.

##### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up.

##### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

##### Returns

A fully functional [UserPreview](api?id=entity-userpreview) object.

<!-- dogehouse.entitities.Room -->
### Room :id=entity-room

?> Implements:  
    `__str__` = name
    `__sizeof__` = count

Represents a dogehouse.tv room.

##### Attributes

* `id` *(string)*: The id of the room.
* `creator_id` *(string)*: The id of the user who created the room.
* `name` *(string)*: The name of the room.
* `description` *(string)*: The description of the room.
* `created_at` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the room was created.
* `is_private` *(bool)*: Wheter or not the room is a private or public room
* `count` *(int)*: The amount of users the room has.
* `users` *(List of [User](api?id=entity-user)s and/or [UserPreview](api?id=entity-userpreview)s)*: A list of users whom reside in this room.

<!-- dogehouse.entitites.Message -->
### Message :id=entity-message

?> Implements:  
    `__str__` = content

Represents a message that gets sent in the chat.

##### Attributes

* `id` *(string)*: The message its id
* `tokens` *(List of dictionaries where the key and value are strings])*: The message content tokens, for if you want to manually parse the message.
* `is_wisper` *(bool)*: Whether or not the message was whispered to the client.
* `created_at` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the message was created.
* `author` *([BaseUser](api?id=entity-baseuser))*: The user who sent the message

<!-- dogehouse.entitites.Message -->
### Context :id=entity-context

Represents a message its context.

##### Attributes

* `client` *([Client](api?id=entity-client))*: The current client.
* `bot` *([Client](api?id=entity-client))*: Alias for `client`.
* `message` *([Message](api?id=entity-message))*: The message that was sent.
* `author` *([BaseUser](api?id=entity-baseuser))*: The message author.

<!-- dogehouse.entitites.Permission -->
### Context :id=entity-permission

Represents a user their permissions

##### Attributes

* `asked_to_speak` *(bool)*: Whether or not the user has requested to speak.
* `is_mod` *(bool)*: Wheter or not the user is a room moderator.
* `is_admin` *(bool)*: Wheter or not the user is a room admin.

## Exceptions :id=exceptions

These are all the custom exceptions that can get raised by certain actions.

### Refference

#### DogehouseException :id=exceptions-dogehouseexception

The base exceptions object.

#### InvalidAccessToken :id=exceptions-invalidaccesstoken

The exception that gets raised when an invalid access token is present.

#### NoConnectionException :id=exceptions-noconnectionexception

The base exceptions object.

#### InvalidSize :id=exceptions-invalidsize

The exception that gets raised when a variable is not within the requested size.

#### NotEnoughArguments :id=exceptions-noenougharguments

Not enough arguments where provided.

#### CommandNotFound :id=exceptions-commandnotfound

Command is not registered.

#### MemberNotFound :id=exceptions-membernotfound

The requested member was not found!

#### CommandAlreadyDefined :id=exceptions-commandalreadydefined

The command has already been defined by another name or alias.
