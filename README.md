# TIRA: Thematic Investment Research Agent

....

## Design specification

The system is based on a microservice design to allow scalability, flexibility and
modularity. This is important in order to meet enterprise-wide usage and for
adaptability to replace or upgrade microservices to keep up with the rapid
technological development in the AI space.

**Research Agent Workers**

* Purpose: Perform thematic investment research and outputs a report for portfolio
  managers.
* Technology: OpenAI Agent SDK, Markdown, Python Celery.
* Interface: Redis message queue through Celery.
* Deployment: As a docker container through `docker compose`

**Task Queue Backend**

* Purpose: API backend and task queue client to submit asynchronous tasks to Research
  Agent Workers and for querying task status and getting task results.
* Technology: Python Celery, FastAPI.
* Interface: REST API, Redis message queue through Celery.
* Deployment: As a docker container through `docker compose`

**Task Queue Broker**

* Purpose: Message transport for distributing and managing tasks to multiple worker
  processes that run across different threads or machines. A worker process will execute
  a Research Agent.
* Technology: Redis.
* Interface: Redis message queue through Celery.
* Deployment: As a docker container through `docker compose`

**Frontend**

* Purpose: Simple UI for users to input an investment theme to be researched,
  observe the research status, and for downloading reports of finished research.
* Technology: Streamlit
* Interface: Browser (HTTP)
* Deployment: As a docker container through `docker compose`

**Tracing and Observability server**

* Purpose: Tracing LLM calls and Agent actions.
* Technology: MLFlow
* Interface: MLFlow SDK
* Deployment: As a docker container through `docker compose`
