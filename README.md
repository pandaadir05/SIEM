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

> Requirements: `Docker`, `Python 3.13` (Recommended, 3.11+ supported), `Node.js` (for UI), `Kafka`, `Elasticsearch`

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

## 🧪 Testing the Setup

After running `docker-compose up -d --build`, you can perform these steps to verify the core components:

1.  **Check Container Status:**
    ```bash
    docker ps
    ```
    You should see containers for `siem_zookeeper`, `siem_kafka`, `siem_elasticsearch`, `siem_kibana`, `siem_indexer`, `siem_correlation_engine`, and `siem_backend_api` running.

2.  **Generate Dummy Logs:**
    Run the dummy log generator script. This will send sample logs to the `logs_raw` Kafka topic.
    ```bash
    # Run this in a separate terminal in the project root
    python ingestion/dummy_generator.py
    ```
    You should see output like `[DummyGen] Sent: {...}`. Let it run for a minute or two, then stop it with `Ctrl+C`.

3.  **Check Logs in Kibana:**
    *   Open Kibana in your browser: [http://localhost:5601](http://localhost:5601)
    *   Navigate to the menu (☰) > Management > Stack Management > Kibana > Index Patterns.
    *   Click "Create index pattern".
    *   Enter `logs` as the index pattern name. It should find the `logs` index created by the indexer.
    *   Select `@timestamp` as the time field.
    *   Click "Create index pattern".
    *   Now go to the menu (☰) > Analytics > Discover.
    *   You should see the logs generated by `dummy_generator.py` appearing here.

4.  **Check Alerts in Kibana:**
    *   Some dummy logs might trigger the "Suspicious Command Prompt" rule.
    *   Create another index pattern named `alerts`.
    *   Select `@timestamp` as the time field.
    *   Go back to Discover and select the `alerts` index pattern.
    *   You might see alerts generated by the correlation engine.

5.  **Check Backend API:**
    *   **Logs Endpoint:** Open [http://localhost:5000/api/logs](http://localhost:5000/api/logs) in your browser or use `curl`. You might need to provide the dummy token (check `ui/backend_api/rbac.py` or `ui/frontend/src/api/client.js` for the current placeholder token).
        ```bash
        # Example using curl with the placeholder token
        curl -H "Authorization: Bearer fake-jwt-token-admin" http://localhost:5000/api/logs
        ```
    *   **Alerts Endpoint:** Open [http://localhost:5000/api/alerts](http://localhost:5000/api/alerts) or use `curl`.
        ```bash
        curl -H "Authorization: Bearer fake-jwt-token-admin" http://localhost:5000/api/alerts
        ```

6.  **Check Frontend (If Running):**
    *   If you started the React frontend (`npm start` in `ui/frontend`), open [http://localhost:3000](http://localhost:3000).
    *   Navigate the UI (e.g., Dashboard, Timeline) to see if data is being displayed. Note that the frontend might require login/authentication setup to be fully functional.

If logs and alerts appear in Kibana and the API endpoints return data, the basic pipeline is working.

---

## 🔧 Troubleshooting

### Kafka Dependency Errors (`ModuleNotFoundError: No module named 'kafka.vendor.six.moves'`)

This error typically occurs with older versions of `kafka-python` on newer Python versions like 3.13.

**Solution:**

The primary fix is to ensure you are using a recent version of `kafka-python`.

1.  **Update `requirements.txt`:** Make sure your `requirements.txt` specifies a recent version, for example:
    ```txt
    # requirements.txt
    kafka-python>=2.1.0 # Use a version >= 2.1.0
    # ... other dependencies
    ```
    *(Note: The explicit `six==1.16.0` dependency is likely no longer needed with newer `kafka-python` versions).*

2.  **Reinstall Dependencies:**
    *   **🐳 Docker Users:** Rebuild the relevant Docker images to include the updated library:
        ```bash
        docker-compose build indexer correlation-engine backend-api # Rebuild services using Python
        docker-compose up -d --build # Or simply this to rebuild everything if needed
        ```
    *   **🏃 Local Environment Users:** Ensure your virtual environment is activated and reinstall dependencies:
        ```bash
        # Activate your virtual environment (e.g., .\.venv\Scripts\activate)
        pip install --upgrade pip
        pip install -r requirements.txt
        ```

3.  **Verify:** Try running the Python script (e.g., `python consumer/indexer.py`) again.

If you still encounter issues after updating `kafka-python`, double-check that you are operating within the correct, activated virtual environment where the updated packages were installed.

### Elasticsearch Connection Issues

If components can't connect to Elasticsearch, ensure:
1. Elasticsearch container is running: `docker ps | grep elasticsearch`
2. You can access it: `curl http://localhost:9200`
3. Environment variables are correct if you've customized the setup

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