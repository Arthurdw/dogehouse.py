Python wrapper for the dogehouse API
====================================

Documentation
-------------

You can find the documentation at `dogehouse.arthurdw.com <http://dogehouse.arthurdw.com/>`_

Installation
------------

``pip install dogehouse``


Example
--------

.. code-block:: python

    from dogehouse import DogeClient, event, command
    from dogehouse.entities import Message


    class Client(DogeClient):
        @event
        async def on_ready(self):
            print(f"Successfully connected as {self.user}!")
            await self.create_room("Hello World!")
        
        @command
        async def foo(self, ctx: Message):
            await self.send("bar")

        
    if __name__ == "__main__":
        Client("YourToken", "YourRefreshToken", prefix="!").run()



Tokens
--------
- Go to https://dogehouse.tv
- Open Developer options (F12 or Ctrl+Shift+I)
- Go to Application > Local Storage > dogehouse.tv
- There lies your TOKEN and REFRESH_TOKEN
