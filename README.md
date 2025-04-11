# 🛡️ Next-Gen SIEM Platform

A powerful, real-time, AI-enhanced **Security Information and Event Management (SIEM)** platform designed to detect, correlate, and respond to modern threats — built with ❤️ by Adir.

---

## 🚀 Key Features

- ✅ **Log Ingestion via Kafka**  
- 🔍 **Elasticsearch Indexing & Search**  
- 🧠 **ML-based Anomaly Detection**  
- 📜 **Sigma Rule Integration for Correlation**  
- 🗃️ **MITRE ATT&CK Technique Tagging**  
- 📈 **Real-Time Alerting & Visualization**  
- 🤖 **LLM-Powered Triage Assistant**  
- 🧪 **SOAR Automation & Playbooks (Coming soon)**  
- 📊 **Beautiful Frontend in React (WIP)**  

---

## 🧱 Project Structure

```
SIEM/
├── ingestion/           → Log agent (sends logs to Kafka)
├── consumer/            → Indexer (reads Kafka, stores to Elasticsearch)
├── correlation/         → Sigma rule engine
├── ml/                  → Anomaly detection
├── llm/                 → GPT/LLM-based alert summarizer
├── rules/               → Sigma rule YAMLs
├── ui/                  → React frontend + backend API
├── test_logs/           → Sample logs (for testing)
├── docker-compose.yml   → All services (Kafka, Zookeeper, Elasticsearch, Kibana)
├── .gitignore           → Exclude build files, logs, etc.
└── README.md            → You’re here
```

---

## ⚡ Quick Start

> Requirements: `Docker`, `Python 3.11+`, `Node.js` (for UI), `Kafka`, `Elasticsearch`

### 🐳 Start Kafka, Elasticsearch, and Kibana:

```bash
docker-compose up -d
```

### 🔁 Ingest Logs (Agent → Kafka):

```bash
python ingestion/agent.py
```

### 🔄 Index Logs (Kafka → Elasticsearch):

```bash
python consumer/indexer.py
```

### 🚨 Run Sigma Correlation Engine:

```bash
python -m correlation.sigma_engine
```

### 🤖 Start LLM Triage Assistant:

```bash
python llm/llm_assistant.py
```

> Make sure to set your `OPENAI_API_KEY` in environment variables before running the LLM service.

---

## 📊 Frontend (React + Backend)

```bash
cd ui/frontend
npm install
npm start
```

Backend API:

```bash
cd ui/backend_api
python app.py
```

---

## 💡 Example Rule (Sigma)

```yaml
title: Suspicious Command Prompt
detection:
  selection:
    CommandLine|contains: "cmd.exe"
  condition: selection
level: high
```

> Sigma rules are stored in `rules/` and dynamically loaded into the correlation engine.

---

## 🧠 Coming Soon

- Real-time stream processing with **Apache Flink**
- Timeline visualizations & investigation graphs
- Full SOAR engine with playbooks
- PDF report generation
- Kubernetes deployment (Helm)
- LLM-powered Chat UI for threat hunting

---

## 📘 License

MIT © 2025 [Adir Shitrit](https://github.com/adirshitrit)

---

## 🙌 Contributing

This is a passion project — feel free to fork, contribute, suggest ideas, or just star the repo ⭐  
You can open issues for ideas, bugs, or feature requests.

---