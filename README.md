# Next-Gen SIEM Monorepo (Massive Edition)

## Overview
This repository contains everything:
- **docker-compose.yml** for Kafka, ES, Kibana
- **Python ingestion** + consumer + correlation
- **Sigma-based** detection, multi-step logic
- **ML** (batch anomaly in Python, optional Spark streaming)
- **SOAR** orchestrator
- **LLM** microservice
- **UI** (Flask + React)
- **Optional** Flink streaming job for advanced correlation

## Prerequisites
- Docker / Docker Compose
- Python 3.9+ (for scripts)
- Node.js (for React UI)
- Java/Scala + Maven if you want to build and run Flink/Spark

## Setup Steps

1. **Start Core Infra**:
   ```bash
   docker-compose up -d
