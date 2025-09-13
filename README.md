# MINI-RAG-APP

This is a minimal implementation of the RAG model for question answering.

## Requirements

- python 3.8 or later

### Install python using Miniconda

1) Download and install MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag-app-env python=3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag-app-env
```

## Installation

### Install the requirements packages

```bash
$ pip insatll -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `API_KEY` value.


## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
