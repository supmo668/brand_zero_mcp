# Brand Zero - Brand Presence Research Tool

A Model Context Protocol (MCP) server application for streamlining brand presence research for marketers.

## Overview

This tool helps marketers analyze their brand's online presence by:

1. Simulating natural search queries that consumers might use to find products in your category (without explicitly mentioning your brand)
2. Running these queries through multiple search engines (OpenAI and Perplexity)
3. Analyzing the search results to evaluate your brand's visibility, competitor mentions, and consumer sentiment

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key with access to gpt-4o-search-preview model
- Perplexity API key with access to sonar-pro model

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your API keys.

## Usage

### Command Line Interface

You can run brand presence analysis directly from the command line:

```bash
python run_workflow.py "Your Brand Name"
```

Options:
- `-o, --output`: Save results to a JSON file
- `-v, --verbose`: Print verbose output including all simulated queries and search result statistics

Example:
```bash
python run_workflow.py "Nike Running Shoes" -v -o results.json
```

### MCP Server

To start the MCP server:

```bash
python main.py
```

The server will start on port 8000 by default (can be changed in .env file).

## Project Structure

- `main.py`: MCP server implementation
- `run_workflow.py`: Command line interface for running the workflow
- `pipeline.py`: Core analysis pipeline implementation
- `models.py`: Data models
- `llm_service.py`: LLM service for interacting with language models
- `llm_providers.py`: Implementation of different search providers
- `utils.py`: Utility functions
- `config.yaml`: Configuration file

## Configuration

The `config.yaml` file contains:

- Logging settings
- Model configurations
- Pipeline parameters
- Prompt templates

## Example Output

The analysis output includes:

1. Summary of brand presence
2. Frequency analysis (how often your brand appears in search results)
3. Competitor analysis
4. Consumer sentiment analysis
5. Strategic recommendations for improving visibility
