# spooky-tarot-card-interpreter
This is a tarot card interpreter made with openai model queries for halloween.


Here are some instructions for how to get the program running. The steps might vary across different systems.

Download the tarot.py program and navigate to the downloads folder.
~~~
cd ~/Downloads
~~~
Look for tarot.py

Create a python environment

~~~
python3 -m venv .venv
~~~

~~~
source .venv/bin/activate
~~~

~~~
python -m pip install --upgrade pip
~~~

You can add or remove packages depending on which api you want to use.

~~~
python -m pip install openai anthropic google-genai
~~~

This is for the openai api
~~~
export OPENAI_API_KEY="paste_your_key_here"
~~~

This is for the anthropic api
~~~
export ANTHROPIC_API_KEY="paste_your_key_here"
~~~

This is for the gemini api 
~~~
export GEMINI_API_KEY="paste_your_key_here"
~~~

Run the program by executing the following command: 
~~~
python tarot_reader_multi_api.py
~~~
