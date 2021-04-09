# Introduction

This is the documentation for the dogehouse python library. This library was created to aid in creating applications that
will utilize the [dogehouse.tv](https://dogehouse.tv) API.

## Prerequisites

The dogehouse python library works with python 3+, but using the latest version of python is recommended. Support for
non LTS python version will be limited.

## Installing

You can get the library from PyPi:

```
python3 -m pip install -U dogehouse
```

Or if you are using windows, use the following command instead:

```
py -3 -m pip install -U dogehouse
```

### Virtual Environments

Sometimes you want to keep libraries from polluting system installs or use a different version of libraries than the
ones installed on the system. You might also not have permissions to install libraries system-wide. For this purpose,
the standard library as of Python 3.3 comes with a concept called “Virtual Environment” s to help maintain these separate
versions.

More information can be found on [Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html).

#### Venv Installation

1. Go to your desired directory:
   ```bash
   $ cd my-directory
   # For unix based systems
   $ python3 -m venv virtual
   # For windows
   $ py -3 -m venv virtual
   ```
2. Activate the virtual environment:
   ```bash
   # For unix based systems
   $ source virtual/bin/activate
   # For windows
   $ virtual\Scripts\activate.bat
   ```
3. Install the dogehouse library like usual:
   ```
   $ pip install -U dogehouse
   ```

## Basic Concepts

The dogehouse python library revolves around the same concepts as discord.py, which includes events. If you are not
familiar with discord.py, an event is something you listen to and then respond to. For example, when a message gets
send in the chat you will receive an event about it to which you can respond.

A quick example to showcase how events work in the dogehouse library:

```py
import dogehouse


class MyClient(dogehouse.DogeClient):
    @dogehouse.event
    async def on_ready(self):
        print(f"Logged on as {self.user.username}")


MyClient("token", "refresh_token").run()
```

The example will print `Logged on as <your username>` when the client has connected successfully to the dogehouse API.
