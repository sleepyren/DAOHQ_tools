# DAOHQ Community Analytics and Image Generation

This repository contains Python scripts developed during my internship to analyze DAO (Decentralized Autonomous Organization) community data and generate informative images. These scripts perform tasks such as scraping Discord server member statistics, conducting sentiment analysis of community reviews, and generating visual representations of DAO data.
Features

## Discord Member Statistics Scraper (discord_scraper.py)
Uses Selenium to scrape online and total member counts from Discord servers.
Stores member statistics in a MongoDB database.
Calculates percentage changes in member counts over various time periods (24 hours, 7 days, 30 days).

## DAO Image Generation (image_generator.py)
Generates images with DAO details including name, mission, financial data, and Discord member counts.
Uses PIL to create and edit images, integrating logos and other visual elements.
Retrieves data from MongoDB to populate image content.

## Requirements

    Python
    MongoDB
    Google Chrome (for Selenium WebDriver)
