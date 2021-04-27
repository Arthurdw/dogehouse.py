.. image:: https://img.shields.io/badge/pypi-dogehouse-blue
 :target: https://pypi.org/project/dogehouse
.. image:: https://img.shields.io/pypi/v/dogehouse
 :target: https://pypi.org/project/dogehouse
.. image:: https://static.pepy.tech/personalized-badge/dogehouse?period=total&units=international_system&left_color=gray&right_color=blue&left_text=Downloads
 :target: https://pepy.tech/project/dogehouse
.. image:: https://img.shields.io/pypi/pyversions/dogehouse
 :target: https://pypi.org/project/dogehouse

Python wrapper for the dogehouse API
====================================

NOTE:
-----

This project is now archived. Because of the latest update of the dogehouse API which changes a lot of things. And general issues with how the library was built.

I'd like to say thank you for all the positive support for this project. It was great while it lasted! ♥

& you are free to fork this repository to build out/release your own library.

**This project gets continued in the dogegarden organisation @ https://github.com/dogegarden/dogehouse.py**

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
