from aider.coders import Coder
from aider.models import Model
from dotenv import load_dotenv
import inspect
load_dotenv(".env")

def print_heart():
    """打印爱心图案"""
    heart = [
        "  ******    ******  ",
        " ********  ******** ",
        "********************",
        " ****************** ",
        "  ****************  ",
        "   **************   ",
        "    ************    ",
        "     **********     ",
        "      ********      ",
        "       ******       ",
        "        ****        ",
        "         **         "
    ]
    for line in heart:
        print(line)

# This is a list of files to add to the chat
fnames = ["fibonacci.py"]

model = Model("deepseek")

# Create a coder object
coder = Coder.create(main_model=model, fnames=fnames)

# 打印爱心
print_heart()

# # This will execute one instruction on those files and then return
# coder.run("make a script that prints hello world")
# coder.run("/tokens")
