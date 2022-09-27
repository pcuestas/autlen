#!/usr/bin/env python3

import os 

cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))

os.system(f"cd {dir_path}") ###########################################

os.system("git add .")

msg = ""
while not msg: msg = input("Enter commit message: ")

os.system(f"git commit -m \"{msg}\"")
os.system(f"git push")

os.system(f"cd {cwd}")      ###########################################
