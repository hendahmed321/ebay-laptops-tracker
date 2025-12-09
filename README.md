# eBay Laptops Price Tracker & Analytics

## Project Overview
An end-to-end data engineering pipeline that automatically collects, processes, and visualizes laptop price data from eBay for market analysis and price tracking.

**Live Dashboard:** [View MongoDB Charts Dashboard](https://charts.mongodb.com/charts-project-0-fqyccyb/dashboards/69328730-0876-40aa-829c-3389f21ca972)

<img width="1349" height="363" alt="charts" src="https://github.com/user-attachments/assets/b383777e-1ce0-47ab-a532-cd4b77314646" />

## Features
- **Automated Data Collection**: Daily scraping of 150+ laptop listings from eBay
- **Data Processing Pipeline**: Cleaning, normalization, and feature extraction (RAM, Storage, CPU, etc.)
- **Cloud Database**: MongoDB Atlas with automated backups and timestamps
- **Interactive Dashboard**: Real-time analytics with MongoDB Charts
- **Scheduled Automation**: Runs 3x daily without manual intervention
- **Error Handling**: Multi-layer fallback system with JSON backups

## Tech Stack
| Technology | Purpose |
|------------|---------|
| **Python** | Main programming language |
| **Selenium** | Web scraping and automation |
| **MongoDB Atlas** | Cloud NoSQL database |
| **PyMongo** | MongoDB Python driver |
| **MongoDB Charts** | Data visualization dashboard |
| **Schedule** | Task scheduling automation |
| **Regex** | Data extraction and cleaning |

## Architecture
<img width="671" height="226" alt="workflow" src="https://github.com/user-attachments/assets/fede8607-1318-40d3-8c79-2c083ab91e57" />
