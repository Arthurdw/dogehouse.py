Python wrapper for the dogehouse API
====================================

Installation
------------

`pip install dogehouse`


Example
--------

.. code-block:: python

    from dogehouse import DogeClient, event
    from dogehouse.entities import Message


    class Client(DogeClient):
        @event
        async def on_ready(self):
            print(f"Successfully connected as {self.user}!")
            await self.create_room("Hello World!")
            
        @event
        async def on_message(self, message: Message):
            if message.content.startswith("!foo"):
                await self.send(f"bar")
                

    if __name__ == "__main__":
        Client("YourToken", "YourRefreshToken").run()
