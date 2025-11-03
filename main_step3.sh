#!/bin/bash


echo "🤖 Now starting the main trading agent..."

# Please create the config file first!!

# python main.py configs/default_day_config.json #run daily config
python main.py configs/default_hour_config.json #run hourly config

echo "✅ AI-Trader stopped"
