# -*- coding: utf-8 -*-
import json

with open('I:/CapitalTrain/metro_line3_official_stops.json', 'r', encoding='utf-8') as f:
    metro_stations = json.load(f)

print('Loaded metro stations:', len(metro_stations))
