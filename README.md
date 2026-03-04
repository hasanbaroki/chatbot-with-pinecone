# Chatbot with Long-Term Memory (Pinecone + OpenAI)

A cloud-native chatbot API with long-term conversational memory, powered by OpenAI GPT-4o-mini and Pinecone vector database. Deployed on Google Cloud Run with full Infrastructure as Code via Terraform.

## Architecture

```
┌────────────┐        ┌──────────────────┐        ┌─────────────┐
│   Client    │──POST──▶  Cloud Run       │──embed─▶  Pinecone   │
│  (any HTTP) │◀─JSON──│  (FastAPI)       │◀─query─│  (Vector DB)│
└────────────┘        │                  │        └─────────────┘
                      │  app/api.py      │
                      │  app/memory.py   │──chat──▶ OpenAI API
                      └──────────────────┘
```

**Flow:**
1. Client sends a message via `POST /chatbot`
2. App retrieves semantically similar past conversations from Pinecone
3. Context + message sent to OpenAI for response generation
4. New exchange stored in Pinecone for future recall
5. Response returned to client

## Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| API Framework    | FastAPI + Uvicorn                   |
| LLM              | OpenAI GPT-4o-mini                  |
| Embeddings       | OpenAI text-embedding-3-small       |
| Vector Database  | Pinecone (Serverless)               |
| Container        | Docker (Python 3.11-slim)           |
| Cloud Platform   | Google Cloud (Cloud Run)            |
| CI/CD            | Google Cloud Build                  |
| IaC              | Terraform                           |
| Secrets          | Google Secret Manager               |

## Project Structure

```
chatbot-with-pinecone/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point (uvicorn runner)
│   ├── api.py               # FastAPI routes (/health, /chatbot)
│   ├── memory.py            # Pinecone vector store logic
│   └── config.py            # Centralized config (pydantic-settings)
├── terraform/
│   ├── main.tf              # Provider config
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── artifact_registry.tf # Artifact Registry repository
│   ├── cloud_run.tf         # Cloud Run service
│   ├── secret_manager.tf    # Secret Manager secrets
│   ├── iam.tf               # IAM bindings for Cloud Build
│   └── terraform.tfvars.example
├── cloudbuild.yaml           # CI/CD pipeline
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

## Local Development

### Prerequisites
- Python 3.11+
- OpenAI API key
- Pinecone API key

### Setup

```bash
# Clone and enter project
git clone <repo-url>
cd chatbot-with-pinecone

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat <<EOF > .env
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
EOF
```

### Run locally

```bash
python -m app.main
# API available at http://localhost:8080
```

## Docker

```bash
# Build
docker build -t chatbot .

# Run
docker run -p 8080:8080 --env-file .env chatbot

# Test health
curl http://localhost:8080/health
```

## Infrastructure (Terraform)

All GCP resources are managed via Terraform:

- **Artifact Registry** — Docker image repository
- **Cloud Run** — Serverless container hosting
- **Secret Manager** — Secure API key storage
- **IAM** — Cloud Build service account permissions

### Provision

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project ID

terraform init
terraform plan
terraform apply
```

> **Note:** After `terraform apply`, manually add secret versions for `OPENAI_API_KEY` and `PINECONE_API_KEY` in Secret Manager. Terraform creates the secret resources but does not store the actual values.

## CI/CD Pipeline

Cloud Build triggers on push to `main`:

1. **Build** — Docker image tagged with `SHORT_SHA` and `latest`
2. **Push** — Image pushed to Artifact Registry
3. **Deploy** — Cloud Run service updated with new image

Secrets are injected at runtime from Secret Manager.

## API Reference

### `GET /health`

Health check endpoint.

**Response:** `200 OK`
```json
{"status": "healthy"}
```

### `POST /chatbot`

Send a message and receive an AI response with long-term memory context.

**Request body:**
```json
{
  "chat_room_id": "room-123",
  "user": "Hasan",
  "message": "What did we talk about yesterday?",
  "timestamp": "2026-03-04T12:00:00Z"
}
```

**Response:** `200 OK`
```json
{
  "chat_room_id": "room-123",
  "user": "Hasan",
  "message": "What did we talk about yesterday?",
  "ai_response": "Yesterday we discussed...",
  "timestamp": "2026-03-04T12:00:01Z"
}
```

## Environment Variables

| Variable          | Description               | Required |
|-------------------|---------------------------|----------|
| `OPENAI_API_KEY`  | OpenAI API key            | Yes      |
| `PINECONE_API_KEY`| Pinecone API key          | Yes      |
| `INDEX_NAME`      | Pinecone index name       | No       |
| `MODEL`           | OpenAI model name         | No       |
| `PORT`            | Server port               | No       |
