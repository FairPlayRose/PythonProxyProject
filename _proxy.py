# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:00:12 2022

@author: Fred PC
"""
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
import json

import os
import sys

sys.path.append(os.getcwd())


class FetchError(Exception):
    
    def __init__(self, code, message) -> None:
        self.code = code
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f'Code:{self.code} -> {self.message}'

def fromFileCards(file=str) -> list[dict]:
    
    with open(file) as a_file:
        list_of_cards = []
        for line in a_file:
            stripped_line = line.strip()
            line_list = stripped_line.split()
            if not bool(line_list):
                continue
            quant = int(line_list[0])
            name = ' '.join(line_list[1::])
            list_of_cards.append({'quant': quant, 'name': name})

    return list_of_cards

def fromListCards(file=str) -> list[dict]:
    list_of_cards = []
    for line in file.splitlines():
        stripped_line = line.strip()
        line_list = stripped_line.split()
        if not bool(line_list):
            continue
        quant = int(line_list[0])
        name = ' '.join(line_list[1::])
        list_of_cards.append({'quant': quant, 'name': name})
    return list_of_cards

class Proxy:
    
    #____________________Attribute_List______________________
    
    Response: None
    ResCode: int
    Name: str
    Url: str
    Mana: str
    Color: str | list[int]
    ProxyImage: None
    QR: None
    TestID: bool
    Layout: str
    
    # obselete
    Proxies: list
    Multid: int
    Set: str
    index: int
    
    #____________________Helper_Functions____________________
    
    # obselete
    def SetExclude(self):
        return ['SLD','SLX']
    
    # obselete
    def NameDomain(self, name = str):
        name_list = name.split(" // ")
        return set(name_list)
    
    def AtCenter(self, bigsize, smallsize) -> int:
        return (bigsize - smallsize) // 2
    
    
    
    # _____________________Run_Funcitons______________________
    
    def __init__(self, name: str, color: None | str | tuple = None) -> None:
        
        #if test_var != None:
        #    pass
            
        
        if color == None:
            color = 'white'
        self.Color = color
        
        new_name = name.replace(" ", "_")
        
        #if test_id == True:
        #    self.Name = new_name
        #    self.IsSplit = True
        #    self.Url = "https://google.com"
        #    self.Mana = test_mana
        #    return
        
        #self.TestID = test_id
        
        self.Response = requests.get(f"https://api.scryfall.com/cards/named?exact={new_name}")
        self.ResCode = self.Response.status_code
        Body = self.Response.json()
        assert self.ResCode == 200, f'Code {self.ResCode}: Card named {name} not found'
        
        #DFClist = ['modal-dfc', 'transform']
        
        self.Name = Body['name']
        self.Url = Body['scryfall_uri']
        self.Layout = Body['layout'] # if Body['layout'] in DFClist else 'normal'
        
        if self.Layout == 'transform':
            self.Mana = Body['card_faces'][0]['mana_cost']
        elif self.Layout == 'modal-dfc':
            self.Mana = Body['card_faces'][0]['mana_cost'] + ' // ' + Body['card_faces'][1]['mana_cost']
        else:
            self.Mana = Body['mana_cost']
        return
    
    # Obselete
    def mtgGET(self) -> None:
        cardValid = [True for card in self.Proxies]
        
        for id, card in enumerate(self.Proxies):
            if card.set in self.SetExclude():
                cardValid[id] = False
            
            if not (hasattr(card, 'multiverse_id') and self.Name in self.NameDomain(card.name)):
                continue
            
            if not ((int(card.multiverse_id) > self.Multid) ^ (card.set == self.Set)):
                continue
            
            self.Multid = int(card.multiverse_id)
            self.index = id
            
            if card.set != self.Set:
                self.Set = card.set
        
        assert any(cardValid) , f"Code 501: Card {self.Name} belongs to Gatherer excluded set and can't be found"
        
        assert self.Multid != 0, f"Code 500: Fetch succesesfull for {self.Name} but no legal card choosen"
        
        card1 = self.Proxies[self.index]
        
        if card1.layout == "split":
            card2 = self.Proxies[self.index+1]
            
            if hasattr(card1, "mana_cost"):
                c1mana = card1.mana_cost
            if hasattr(card1, "mana_cost"):
                c2mana = card2.mana_cost
            
            self.Mana = hasattr(card1, "mana_cost") * c1mana + (hasattr(card1, "mana_cost") and hasattr(card2, "mana_cost")) * " // " + hasattr(card2, "mana_cost") * c2mana
            
        else:
            if hasattr(card1, "mana_cost"):
                self.Mana = card1.mana_cost
            else:
                self.Mana = ""
        return
    
    def makeQR(self) -> None:
        self.QR = qrcode.QRCode(
                version=1,
                box_size=15,
                border=4,
            )
        self.QR.add_data(self.Url)
        self.QR.make(fit = True)
        self.QR = self.QR.make_image(fill_color="black", back_color="white").resize((675,675))
        
        return
    
    def Construct(self):
        
        here = os.path.abspath(os.getcwd())
        self.ProxyImage = Image.open(here + "\\data\\Card_back.png")
        mask = Image.new(mode='RGB', size=(710,996), color=self.Color)
        
        Proxysizex, Proxysizey  = self.ProxyImage.size
        QRsizex, QRsizey = self.QR.size
        Masksizex, Masksizey = mask.size
        
        _setup = None
        if _setup == None or self.TestID == True:
            with open("Layout.json") as f:
                _setup = json.load(f)

        "Check the constructor has all nesesary components before executing"
        
        self.ProxyImage.paste(mask, (20, 25))
        draw = ImageDraw.Draw(self.ProxyImage)
        font = ImageFont.truetype(here + "\\data\\beleren-bold.ttf", size = _setup["text-size"])
        
        if self.Layout == "transform" or self.Layout == "modal-dfc":
            name1, name2 = self.Name.split(" // ")
            draw.text(
                    (50, _setup["text-height"] ), 
                    name1 + " // ", 
                    tuple(_setup["font-color"]), 
                    font=font, 
                    stroke_width = _setup["stroke-width"], 
                    stroke_fill = tuple(_setup["stroke-fill"])
                    )
            draw.text(
                    (50, _setup["text-height"] + 50), 
                    name2, 
                    tuple(_setup["font-color"]), 
                    font=font, 
                    stroke_width = _setup["stroke-width"], 
                    stroke_fill = tuple(_setup["stroke-fill"])
                    )
            draw.text(
                    (50, _setup["text-height"] + 100), 
                    self.Mana, 
                    tuple(_setup["font-color"]), 
                    font=font, 
                    stroke_width = _setup["stroke-width"], 
                    stroke_fill = tuple(_setup["stroke-fill"])
                    )
        else:
            draw.text(
                    (50, _setup["text-height"] ), 
                    self.Name, 
                    tuple(_setup["font-color"]), 
                    font=font, 
                    stroke_width = _setup["stroke-width"], 
                    stroke_fill = tuple(_setup["stroke-fill"])
                    )
            draw.text(
                    (50, _setup["text-height"] + 50), 
                    self.Mana, 
                    tuple(_setup["font-color"]), 
                    font=font, 
                    stroke_width = _setup["stroke-width"], 
                    stroke_fill = tuple(_setup["stroke-fill"])
                    )
        self.ProxyImage.paste(self.QR, (self.AtCenter(Proxysizex, QRsizex), _setup["qr-height"]))
        return self.ProxyImage


