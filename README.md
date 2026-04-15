# TIRA: Thematic Investment Research Agent

## Motivation

New investment themes such as Quantum Computing, Clean Energy, and Agentic AI emerge
faster than ever before. The rapid evolution of technology has made it increasingly
more difficult for investment portfolio managers to produce timely and comprehensive
thematic investment research across emerging sectors. TIRA solves this by being a
scalable and flexible research platform, automatically conducting
institutional-quality thematic investment research and generating reports for
portfolio managers to consume.

## What the Thematic Investment Research covers

* Research for understanding market dynamics.
* Research for evaluating investment opportunities.
* Research for identifying and evaluating company exposure.
* Comparing financials for the top two most prospective companies to invest in.

## How the Thematic Investment Research is evaluated

Success criteria:

1. Grounded in reality and claims supported by sources.
2. Sources are high-quality and credible.
3. Sufficient coverage of requested information.
4. Facts and numbers are exact match from source and verifiable.

Test cases:

* A measurable task that defines input instructions and expected output/behavior
  for a Research Agent.
* Test cases may also require to evaluate the Agent traces.
* Test cases are typically composed into collections termed as evaluation datasets.
* Each test case may contain multiple graders or scorers.

Grading/Scoring types:

* Code-based: String matching, binary tests, specific conditions.
* Model-based: Language judging, guideline judging, behaviour judging, rubric scoring,
  nuanced conditions.
* Human-based: None (For future work)

Evaluation harness:

* MLFlow SDK is used for defining, running and orchestrating evaluations.

Guardrails:

* Validating user input and model output for relevance and safety.
* OpenAI Agent SDK is used to define guardrails.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- An API key for an OpenAI-compatible LLM provider

### Setup

1. Clone the repository and create your environment file:

```bash
cp .env.example .env
```

2. Add your API key to `.env`:

```
OPENAI_API_KEY=sk-...
```

Optionally, set a custom base URL for the LLM provider. This defaults to
`https://api.marketplace.novo-genai.com/v1`:

```
OPENAI_BASE_URL=https://api.marketplace.novo-genai.com/v1
```

3. Build and start all services:

```bash
docker compose up --build
```

### Usage

| Service   | URL                   |
|-----------|-----------------------|
| Frontend  | http://localhost:8501 |
| REST API  | http://localhost:8000 |
| MLflow UI | http://localhost:5000 |

Open the frontend to submit an investment theme and download the generated report.

To submit a research task via the API directly:

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"theme": "Quantum Computing"}'
```

A research task is expected to take between ~250 seconds to ~500 seconds.

### Running Tests

Tests are written using `pytest` and test cases are written to verify that the
thematic investment research flow runs end-to-end and that all microservices
integrate correctly.

With all services running:

```bash
uv run pytest tests/ -m e2e -v
```

## Design specification

TIRA is a Python based solution managed with `uv` and `docker compose`.

The TIRA system follows a microservice design to allow scalability, flexibility and
modularity. This is important in order to meet enterprise-wide usage and for
adaptability to replace or upgrade microservices to keep up with the rapid
technological development in the AI space.

### Microservices

**Research Agent Worker**

* Purpose: Perform thematic investment research on a given theme and outputs a report
  for portfolio managers to consume.
* Technology: OpenAI Agent SDK, Markdown, Python Celery.
* Interface: Redis message queue through Celery.
* Deployment: As a docker container through `docker compose`

**Task Queue Backend**

* Purpose: API backend and task queue client to submit asynchronous tasks to Research
  Agent Workers and for querying task status and getting task results.
* Technology: Python Celery, FastAPI.
* Interface: REST API, Redis message queue through Celery.
* Deployment: As a docker container through Docker Compose

**Task Queue Broker**

* Purpose: Message transport for distributing and managing tasks to multiple worker
  processes that run across different threads or machines. A worker process will execute
  a Research Agent.
* Technology: Redis.
* Interface: Redis message queue through Celery.
* Deployment: As a docker container through Docker Compose

**Frontend**

* Purpose: Simple UI for portfolio managers to input an investment theme to be
  researched, observe the research status, and for downloading reports of finished
  research.
* Technology: Streamlit
* Interface: Browser (HTTP)
* Deployment: As a docker container through Docker Compose

**Tracing, Observability, and Evaluation server**

* Purpose: Tracing LLM calls and Agent actions for observability and
  performance evaluation.
* Technology: MLFlow
* Interface: MLFlow SDK
* Deployment: As a docker container through Docker Compose

### Technology choice motivation

* OpenAI Agent SDK had a good developer experience and offers a lot of flexibility.
* Markdown is the industry standard for human and computer readable text.
* Python Celery is the most mature task queue system in Python.
* Redis is lightweight and very high-performant.
* Streamlit is simple and compatible with Python.
* MLFlow is lightweight and easy to self-host.
