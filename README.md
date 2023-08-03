# TCP-Chat #

## General info 

The TCP-Chat application allows users to communicate with one another via desktop or console app. The user, after writing his nickname, has the ability to write and send messages to other users.



## Technologies 

Python 3.10 (Libraries: socket, speech_recognition, threading, queue, enum, pytest, unittest)<br>
PyQt6 (used as an example of a GUI app)



## Setup

* `git clone https://github.com/KatarzynaDudziak/tcp-chat.git`
* `python -m venv venv`
* Windows `venv\Scripts\activate.bat`
* Linux, MacOS X `source bin/activate`
* `pip install -r requirements.txt`



## Usage 

After preparing the setup, you can easily start the app in two steps: first of all, you have to start the server by running `run_server.app` in your console, and after that, you need to run the app by running `run_app.bat` in the second console window.
