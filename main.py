from aider.coders import Coder
from aider.models import Model
from dotenv import load_dotenv
import inspect
load_dotenv(".env")
# This is a list of files to add to the chat
fnames = ["fibonacci.py"]

model = Model("deepseek")

# Create a coder object
coder = Coder.create(main_model=model, fnames=fnames)


# # This will execute one instruction on those files and then return
# coder.run("make a script that prints hello world")
# coder.run("/tokens")
