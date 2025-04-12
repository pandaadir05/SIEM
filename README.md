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

> Requirements: `Docker`, `Python 3.11` (Recommended, 3.11+ supported but newer versions like 3.13 may have library compatibility issues), `Node.js` (for UI), `Kafka`, `Elasticsearch`

### 🐳 Run Services with Docker (Recommended)

This is the easiest way to get all components running.

```bash
# Build and start all services defined in docker-compose.yml
docker-compose up -d --build
```

This will start Zookeeper, Kafka, Elasticsearch, Kibana, and the custom Python services (indexer, correlation-engine, backend-api) inside Docker containers.

### 🏃 Run Components Locally (Alternative)

If you prefer to run Python components directly on your host machine:

1.  **Start Infrastructure:** Ensure Docker is running and start the core infrastructure:
    ```bash
    docker-compose up -d zookeeper kafka elasticsearch kibana
    ```

2.  **Set up Python Environment:** Create and activate a virtual environment, then install dependencies:
    ```bash
    # Navigate to the project root directory
    cd path/to/SIEM

    # Create virtual environment
    python -m venv .venv

    # Activate (Windows)
    .\.venv\Scripts\activate
    # Activate (macOS/Linux)
    # source .venv/bin/activate

    # Install requirements
    pip install -r requirements.txt
    ```

3.  **Run Python Scripts (in separate terminals):**
    *   **Ingest Logs (Agent → Kafka):**
        ```bash
        python ingestion/agent.py
        ```
        *(Or use `dummy_generator.py` for testing)*
        ```bash
        # python ingestion/dummy_generator.py
        ```
    *   **Index Logs (Kafka → Elasticsearch):**
        ```bash
        python consumer/indexer.py
        ```
    *   **Run Sigma Correlation Engine:**
        ```bash
        # Note: The command in docker-compose uses -m, adjust if needed based on your structure
        python correlation/correlation_engine.py
        ```
    *   **Start LLM Triage Assistant (Optional):**
        ```bash
        # Make sure to set your OPENAI_API_KEY environment variable if using OpenAI
        python llm/llm_assistant.py
        ```
    *   **Start Backend API:**
        ```bash
        # Ensure you are in the SIEM root directory for imports to work
        python ui/backend_api/app.py
        ```

### 📊 Frontend (React)

```bash
cd ui/frontend
npm install
npm start
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

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