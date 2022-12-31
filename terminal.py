from run import run
from Error import KeyboardInterruptErr
import sys

while True:
    try:
        Code = input("chavez language > ")
        if Code in " \t":
            continue
        print(run(Code))
    except (KeyboardInterrupt, EOFError):
        exit()
        print(KeyboardInterruptErr())
