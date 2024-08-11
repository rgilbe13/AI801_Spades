#!/bin/bash

cat CommonSpades.py >> All.py
echo "" >> All.py
cat Card.py >> All.py
echo "" >> All.py
cat Players.py >> All.py
echo "" >> All.py
cat MiniMaxSearch.py >> All.py
echo "" >> All.py
cat MinMaxAlphaBeta.py >> All.py
echo "" >> All.py
cat MiniMaxBreadthFirst.py >> All.py
echo "" >> All.py
cat Game.py >> All.py
echo "" >> All.py
cat Main.py >> All.py

sed -i '/import \*/d' All.py