# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 12:13:01 2022

@author: Fred PC
"""

from datetime import datetime

now = datetime.now()

current_time = now.strftime("%Y-%m-%d-%H%M%S")

import os
import sys

sys.path.append(os.getcwd())

from _ui import ui
from _proxy import Proxy

def main() -> None:
    ui(current_time)
    return

def test() -> None:
    "Liliana, Heretical Healer"
    "Dowsing Dagger"
    
    proxy = Proxy("Dowsing Dagger")
    proxy.makeQR()
    image = proxy.Construct()
    image.show()
    return

if __name__ == '__main__':
    main()
    
    