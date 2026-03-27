# 📈 Crypto Trading Dashboard (SimiPulse)

A professional-grade, real-time cryptocurrency charting application inspired by TradingView. This project visualizes live and historical market data using a modern cloud-native architecture.

## 🚀 Features
- **Real-time Data:** Live price updates powered by Binance WebSocket/API data.
- **Professional Charts:** High-performance candlestick charts using `lightweight-charts`.
- **Historical Data:** Access long-term historical data fetched from AWS S3.
- **Dynamic Search:** Autocomplete search featuring all Binance USDT trading pairs.
- **Multiple Timeframes:** Seamlessly switch between 1m, 5m, 1h, and 1d views.
- **Secure Auth:** Integrated user authentication via **AWS Cognito Hosted UI**.
- **Live Watchlist:** Sidebar to monitor favorite assets with real-time price tracking.

## 🛠 Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript.
- **Charting:** Lightweight Charts (by TradingView).
- **Backend/Ingestor:** Python-based data collectors running on **Kubernetes (K3s)**.
- **Infrastructure:** - **AWS EC2:** Hosting the Kubernetes cluster.
    - **AWS S3:** Long-term storage for historical market data.
    - **Redis:** Real-time cache for live price updates.
    - **AWS CloudFront:** Content delivery and HTTPS termination.
    - **AWS Cognito:** Managed user identity and login.

## 🏗 Architecture
1. **Data Ingestor:** A K3s pod constantly fetches data from Binance and pushes it to Redis (for speed) and S3 (for history).
2. **API Layer:** Serves requests from the frontend, stitching together live and historical data.
3. **Frontend:** A clean, responsive UI hosted on GitHub Pages, communicating securely with the AWS backend via CloudFront.
