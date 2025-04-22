# Web Research Agent Documentation

## Overview

The Web Research Agent is an AI-powered web research tool that automates the process of searching the web, extracting relevant information, and synthesizing it into comprehensive reports. This document provides a detailed explanation of the system architecture, components, and implementation details.

## System Architecture

The application follows a modular architecture with the following main components:

1. **Web Interface (Flask)**: Handles user requests and displays results
2. **Research Agent**: Coordinates the research process
3. **Tool Components**: Specialized tools for different aspects of web research
4. **AI Integration**: Uses Google's Gemini model for content analysis and synthesis

## Core Components

### 1. Flask Web Application (`app.py`)

The web application is built using Flask and provides:
- A simple web interface for users to input research queries
- API endpoints for processing research requests
- Request queue management to handle concurrent requests
- Worker threads to process requests asynchronously

Key features:
- Maintains a persistent research agent to handle multiple queries
- Implements request timeouts to prevent long-running queries
- Manages worker threads to control server load

### 2. Research Agent (`agent.py`)

The `WebResearchAgent` class orchestrates the entire research process:
- Analyzes user queries to determine search strategy
- Coordinates web searches across multiple search terms
- Extracts and analyzes content from search results
- Synthesizes information into comprehensive reports

The research process follows these steps:
1. Query analysis to extract main topics and search terms
2. Web search using the generated search terms
3. Content extraction from search results
4. Content analysis for relevance to the query
5. Information synthesis into a final report

### 3. Tool Components (`tools.py`)

#### WebSearchTool
- Uses SerpAPI to search the web
- Implements rate limiting to prevent API throttling
- Returns structured search results

#### WebScraperTool
- Extracts content from web pages using BeautifulSoup
- Handles various error conditions during scraping
- Cleans and formats extracted text

#### ContentAnalyzerTool
- Uses Google's Gemini model to analyze content relevance
- Implements rate limiting for API calls
- Returns relevance scores and extracted relevant content

#### NewsAggregatorTool
- Searches for news articles on specific topics
- Uses SerpAPI's news search functionality
- Returns structured news results

## Error Handling and Limitations

### Fixed Issues

1. **Memory Management**: Implemented garbage collection to prevent memory leaks
2. **Query Persistence**: Modified the application to maintain a persistent research agent
3. **Rate Limiting**: Added rate limiting to prevent API throttling
4. **Error Handling**: Improved error handling throughout the application

### Current Limitations

1. **API Dependency**: The application relies on external APIs (SerpAPI and Google Gemini)
2. **Content Extraction**: Web scraping can be unreliable for some websites with complex structures
3. **Processing Time**: Complex queries can take significant time to process
4. **Concurrent Requests**: Limited to 3 concurrent requests to manage server load

The primary limitation with using only one website search is that the diversity of sources is reduced, which may impact the comprehensiveness of the research. However, this approach is more efficient and reduces API usage.

## Configuration

The application uses environment variables for configuration:
- `SERPAPI_KEY`: API key for SerpAPI
- `GEMINI_API_KEY`: API key for Google's Gemini model
- `PORT`: Port for the web server (defaults to 8080)

## Deployment

The application is designed to be deployed on Render, which provides:
- Easy deployment from GitHub
- Automatic scaling
- HTTPS support
- Free tier for testing and development

## Future Improvements

Potential areas for improvement include:
1. Adding support for more search engines
2. Implementing caching to improve performance
3. Adding user authentication
4. Improving the web interface with real-time updates
5. Adding support for file uploads and downloads
