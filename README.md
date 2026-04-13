# TIRA: Thematic Investment Research Agent

## Motivation

New investment themes such as Quantum Computing, Clean Energy, and Agentic AI emerge
faster than ever before. The rapid evolution of technology has made it increasingly
more difficult for investment portfolio managers to produce timely and comprehensive
thematic investment research across emerging sectors. TIRA solves this by being a
scalable and flexible research platform, automatically conducting
institutional-quality thematic investment research and generating reports for
portfolio managers to consume.

## Design specification

The system is based on a microservice design to allow scalability, flexibility and
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
