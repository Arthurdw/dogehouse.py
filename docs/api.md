# API Reference

This is the documentation for the whole library.

## Version Related Info

`dogehouse.__version__`
A string representation of the version which follows the [Semantic Version 2.0.0 Guidelines](https://semver.org/). For example `1.0.0`.

<!-- dogehouse.DogeClient -->
## DogeClient([Client](api?id=entity-client)) :id=dogeclient

Represents your Dogehouse client.

#### Arguments

* `token` *(string)*: Your super secret client token.
* `refresh_token` *(string)*: Your super secret client refresh token.
* `room` *(integer, optional)*: The room your client should join. Defaults to None.
* `muted` *(bool, optional)*: Wether or not the client should be muted. Defaults to False.
* `reconnect_voice` *(bool, optional)*: When the client disconnects from the voice server, should it try to reconnect. Defaults to False.
* `prefix` *(List of strings or a string, optional)*: The bot prefix.

## Entitities

!> All of these entitities should not be manually created by the client. These are inteded to be created by the [DogeClient](api?id=dogeclient)

### Client :id=entity-client

The base client. All these attributes are accessable using the [DogeClient](api?id=dogeclient).

#### Attributes

* `user` *([User](api?id=entity-user))*: The client its user object.
* `room` *([Room](api?id=entity-room))*: The current room in wich the Client resides. Is `None` if no room has been joined.
* `rooms` *(List of [Room](api?id=entity-room)s)*: A collection of all the rooms which the client has cached. This gets fetched automatically if no room has been joined. You can also update this using the `async DogeClient.get_top_public_rooms` method.
* `prefix` *(List of strings)*: A collection of prefixes to which the client should respond.

<!-- dogehouse.entitites.BaseUser -->
### BaseUser :id=entity-baseuser

?> Implements:  
    `__str__` = username

Represents the most basic information of a fetched user.

#### Attributes

* `id` *(string)*: The user their id.
* `username` *(string)*: The username of the user. *(Their mention name)*
* `displayname` *(string)*: The display name of the user.
* `avatar_url` *(string)*: The user their avatar URL.

#### Methods

##### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=entity-baseuser-convert

Convert an argument (id, username, displayname) into a [BaseUser](api?id=entity-baseuser) object.

###### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up. 

###### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

###### Returns

A fully functional [BaseUser](api?id=entity-baseuser) object.

<!-- dogehouse.entitites.User -->
### User([BaseUser](api?id=entity-baseuser)) :id=entity-user

?> Implements:  
    `__str__` = username

Represents a dogehouse.tv user.

#### Attributes

* `id` *(str)*: The user their id.
* `username` *(str)*: The username of the user. (Their mention name)
* `displayname` *(str)*: The displayname of the user.
* `avatar_url` *(str)*: The user their avatar URL.
* `bio` *(str)*: The user ther biography.
* `last_seen` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the user was last online.
* `online` *(bool)*: Whether or not the user is currently online
* `following` *(bool)*: Wheter or not the client is following this user.
* `room_permissions` *([Permission](app?id=entity-permission))*: The user their permissions for the current room.
* `num_followers` *(int)*: The amount of followers the user has.
* `num_following` *(int)*: The amount of users this user is following.
* `follows_me` *(bool)*: Wether or not the user follows the client.
* `current_room_id` *(str)*: The user their current room id.

#### Methods

##### to_base_user(): :id=entity-user-to_base_user

Convert a user object to a [BaseUser](api?id=entity-baseuser) object.
This is intended for internal use (Convertors), as you can access all baseuser properties from the user object.

###### Returns

The newly created [BaseUser](api?id=entity-baseuser) object, which is derived from the current object.

##### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=entity-user-convert

Convert an argument (id, username, displayname) into a [User](api?id=entity-user) object.

###### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up. 

###### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

###### Returns

A fully functional [User](api?id=entity-user) object.

<!-- dogehouse.entitites.UserPreview -->
### UserPreview :id=entity-userpreview

?> Implements:  
    `__str__` = displayname

Represents a userpreview from the [`Client.rooms`](api?id=entity-client) users list.

#### Attributes

* `id` *(string)*: The user their id.
* `displayname` *(string)*: The display name of the user.
* `num_followers` *(integer)*: The amount of followers the user has.

#### Methods

##### `async` convert([ctx](api?id=entity-context), [param](https://docs.python.org/3/library/inspect.html#inspect.Parameter), argument): :id=entity-baseuser-convert

Convert an argument (id, username, displayname) into a [UserPreview](api?id=entity-userpreview) object.

###### Arguments

* `ctx` *([Context](api?id=entity-context))*: The context object.
* `param` *([inspect.Parameter](https://docs.python.org/3/library/inspect.html#inspect.Parameter))*: The param attribute, to check for a default value.
* `argument` *(string)*: The argument that should be looked up.

###### Raises

* [`MemberNotFound`](api?id=exceptions-membernotfound): Gets thrown when no member got found.

###### Returns

A fully functional [UserPreview](api?id=entity-userpreview) object.

<!-- dogehouse.entitities.Room -->
### Room :id=entity-room

?> Implements:  
    `__str__` = name
    `__sizeof__` = count

Represents a dogehouse.tv room.

###### Attributes

* `id` *(str)*: The id of the room.
* `creator_id` *(str)*: The id of the user who created the room.
* `name` *(str)*: The name of the room.
* `description` *(str)*: The description of the room.
* `created_at` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the room was created.
* `is_private` *(bool)*: Wheter or not the room is a private or public room
* `count` *(int)*: The amount of users the room has.
* `users` *(List of [User](api?id=entity-user)s and/or [UserPreview](api?id=entity-userpreview)s)*: A list of users whom reside in this room.

<!-- dogehouse.entitites.Message -->
### Message :id=entity-message

?> Implements:  
    `__str__` = content

Represents a message that gets sent in the chat.

###### Attributes

* `id` *(str)*: The message its id
* `tokens` *(List of dictionaries where the key and value are strings])*: The message content tokens, for if you want to manually parse the message.
* `is_wisper` *(bool)*: Whether or not the message was whispered to the client.
* `created_at` *([datetime](https://docs.python.org/3/library/datetime.html#datetime-objects))*: When the message was created.
* `author` *([BaseUser](api?id=entity-baseuser))*: The user who sent the message

<!-- dogehouse.entitites.Message -->
### Context :id=entity-context

Represents a message its context.

###### Attributes

* `client` *([Client](api?id=entity-client))*: The current client.
* `bot` *([Client](api?id=entity-client))*: Alias for `client`.
* `message` *([Message](api?id=entity-message))*: The message that was sent.
* `author` *([BaseUser](api?id=entity-baseuser))*: The message author.

<!-- dogehouse.entitites.Permission -->
### Context :id=entity-permission

Represents a user their permissions

###### Attributes

* `asked_to_speak` *(bool)*: Whether or not the user has requested to speak.
* `is_mod` *(bool)*: Wheter or not the user is a room moderator.
* `is_admin` *(bool)*: Wheter or not the user is a room admin.
