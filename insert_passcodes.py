# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:22:04 2017

@author: Donzok
"""
import sqlite3
from datetime import datetime

passcodes = ["bletchley6bw79uu3", "acv94denial963pq", "80JDFITMAR", "NLTWENTY17", "uvjs8hny1796ypzd", "hzcc8hny1725gphq", "2gpb8morej9w7x", "pbpp7hny1737vwxy", "nngs2hny1756nscf", "xhtz7hny1777rffd", "vhzp9hny1738urfo", "scrp9hny1754fdvb", "wfuj7hny1794ohvv", "ppan5hny1779dfka", "xkrq7tq5gy68kkjg", "mxnt2hny1776gnky", "xxah8hny1754ceuq", "3ouv7wu5a4", "2973carrie98", "algorithm9ek27ux3", "alignment9nb75yo5", "artifact3ne73hh3", "artifact4tt67xg9", "blue2xc26da2", "cassandra3wh77rg4", "cern2vb46cn7", "creative3nc46wp7", "creative3vk97yv4", "creativity2pc98zp5", "creativity4pb44pf6", "cube8mk95jj7", "deaddrop6bf98mr2", "deaddrop7dt73am6", "devra2gt69qx7", "evolution2gu76gm3", "ezekiel3xh34ug4", "farlowe2ft72ym5", "field4mo46jx6", "glyph6yt84kt8", "ingress3nd85fu9", "inveniri2he69ar3", "jackland4dz47yf6", "jarvis2kn66cz2", "johnson4yn13db2", "lightman4tm34zf3", "message6ca48vf7", "minotaur8bb28et5", "ni7up28fu6", "powercube5yn73em6", "roland7br76tp5", "spacetime4je35kf5", "susanna3ku75cm9", "susanna7og34vw3", "timezero2qm72ut8", "vi2jo15nd0", "vi9uh67mo6", "ni9gq92to9", "80jdfitmar", "alignment3qh24up8", "lvboynxaie", "5NOY8NNT5N"]

conn = sqlite3.connect('files/passcodes.db')
    
cursor = conn.cursor()
    
cursor.execute('''CREATE TABLE IF NOT EXISTS passcodes (passcode  text primary key, date text, user text)''')
    
for passcode in passcodes:
    cursor.execute('''insert into passcodes values(?, ?, ?)''', (passcode, datetime.now().isoformat(), 'd0nzok'))
    
conn.commit()

conn.close()