# 📈 Crypto Trading Dashboard (SimiPulse)

A professional-grade, real-time cryptocurrency charting application inspired by TradingView. This project visualizes live and historical market data using a modern, cost-optimized cloud-native architecture.

## 🚀 Features
- **Real-time Data:** Live price updates powered by Binance WebSocket/API data.
- **Professional Charts:** High-performance candlestick charts using `lightweight-charts`.
- **Historical Data:** Access long-term historical data fetched seamlessly from AWS DynamoDB.
- **Dynamic Search:** Autocomplete search featuring all Binance USDT trading pairs.
- **Multiple Timeframes:** Seamlessly switch between 1m, 15m, 1h, 4h, 1D, 1W, and 1M views.
- **Secure Auth:** Integrated user authentication via **AWS Cognito Hosted UI**.
- **Live Watchlist:** Sidebar to monitor favorite assets with real-time tracking.
- **Price Alerts:** Set custom target prices and receive automated status tracking (Active/Triggered).

## 🛠 Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Hosted on GitHub Pages).
- **Charting:** Lightweight Charts (by TradingView).
- **Backend/Ingestor:** Python-based (`asyncio`) data collectors containerized with Docker.
- **Serverless API:** AWS Lambda and Amazon API Gateway for stateless operations.
- **Infrastructure:** - **AWS EC2:** Hosting the real-time data ingestor (`tickergrab`) and self-hosted Redis.
  - **AWS DynamoDB:** Persistent NoSQL storage (Single Table Design) for market history and user configurations.
  - **Redis:** In-memory cache serving as a high-speed buffer for live price updates.
  - **AWS CloudFront:** Content delivery and secure routing.
  - **AWS Cognito:** Managed user identity, login, and JWT-based access control.
  - **AWS CloudWatch:** Telemetry and system monitoring.

## 🏗 Architecture
1. **Data Ingestor:** A Dockerized Python service on EC2 constantly fetches data from Binance. It pushes live data to Redis (for microsecond latency) and saves closed candles to DynamoDB (for historical persistence). It includes an automated REST API backfill mechanism.
2. **API Layer:** AWS API Gateway and AWS Lambda serve frontend requests (Watchlist management, Alerts setup, Historical data queries) utilizing a highly scalable Pay-as-you-go model.
3. **Frontend:** A clean, responsive UI hosted statically on GitHub Pages, communicating securely with the AWS backend using JWT authorization.
