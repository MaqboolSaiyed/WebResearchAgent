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
4. **Concurrent Requests**: Increased from 3 to 5 concurrent requests on Vercel deployment

#### Single Website Result Issue
Previously, when deployed on Render's free tier with limited resources (0.1 CPU, 512MB RAM) and a 10-second timeout, the application often returned results from only one website due to:
- Insufficient time to process multiple search results before timeout
- Limited memory preventing storage of multiple website contents
- CPU constraints slowing down content processing

The Vercel deployment with increased resources (0.6 CPU, 1026MB RAM) and 60-second timeout resolves these issues by:
- Allowing more time to process multiple search results
- Providing sufficient memory to store and analyze content from multiple websites
- Offering more CPU power for faster content processing and analysis
- Supporting more concurrent requests (increased from 3 to 5)

## Configuration

The application uses environment variables for configuration:
- `SERPAPI_KEY`: API key for SerpAPI
- `GEMINI_API_KEY`: API key for Google's Gemini model
- `PORT`: Port for the web server (defaults to 8080)

## Deployment

### Render Deployment
The application can be deployed on Render, which provides:
- Easy deployment from GitHub
- Automatic scaling
- HTTPS support
- Free tier for testing and development (0.1 CPU, 512MB RAM)
- Default timeout of 10 seconds

### Vercel Deployment
The application is now optimized for deployment on Vercel with the following specifications:
- **CPU Allocation**: 0.6 CPU (6x more than Render's free tier)
- **Memory**: 1026MB RAM (2x more than Render's free tier)
- **Timeout**: 60 seconds (increased from the default 10 seconds)

To deploy on Vercel:
1. Connect your GitHub repository to Vercel
2. Configure the following settings:
   - Framework Preset: Flask
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `./`
   - Install Command: `pip install -r requirements.txt`
3. Add your environment variables (GEMINI_API_KEY and SERPAPI_KEY) in the Vercel dashboard
4. Set the Function Execution Timeout to 60 seconds in the Vercel project settings

The Vercel deployment offers significantly better performance with higher resource limits and longer timeout periods, which helps resolve the issue of getting results from only one website.

### Deployed Instance

The Web Research Agent is currently deployed and accessible at:
[https://webresearchagent.onrender.com/](https://webresearchagent.onrender.com/)

This instance is running on Render's free tier with the following resource constraints:
- 0.1 CPU
- 512MB RAM

These constraints have been addressed through code optimizations including:
- Reduced search term limits
- Memory management with garbage collection
- Rate limiting to prevent CPU spikes
- Simplified processing to reduce resource usage

## Decision-Making Process

The WebResearchAgent follows a structured, step-by-step decision-making process to efficiently gather and synthesize information from the web while operating within strict resource constraints (0.1 CPU, 512MB RAM). Here's a detailed breakdown of how the agent makes decisions:

### 1. Query Analysis

When a user submits a query, the agent first analyzes it to understand intent and determine the optimal search strategy:

- The agent uses the Gemini model to break down the query into structured components:
  - Main topic
  - Key aspects
  - Content type
  - Search terms
- For complex topics (like quantum computing), it breaks them down into specific subtopics
- For very short queries (like "advancement of AI"), it expands them with related concepts
- The agent limits search terms to 1-2 terms maximum to conserve resources
- If the model fails to parse the query, it falls back to using the original query as the search term

### 2. Search Parameter Adjustment

Before searching, the agent dynamically adjusts search parameters based on query complexity:

- For very short queries (fewer than 3 words), it increases results per term and enables query expansion
- For complex queries (more than 10 words or containing terms like "quantum", "physics", etc.), it focuses the search
- For standard queries, it uses default parameters
- All parameters respect the resource constraints (max_search_terms, max_results_per_term, etc.)
- For educational topics, the agent focuses on .edu sites to improve source quality

### 3. Web Search Execution

The agent performs web searches using the optimized search terms:

- It processes each search term sequentially with rate limiting (1-second delay between terms)
- For each term, it either searches the web or aggregates news based on the query type:
  - Standard web search uses the WebSearchTool for general information
  - News-related queries use the NewsAggregatorTool to fetch recent articles
- It applies null checks on search terms and results to prevent errors
- It filters and deduplicates results to ensure quality and resource efficiency
- The agent strictly limits results to the configured maximum (max_total_results)
- For very short queries, it adds time-based filters to get more recent and relevant results

### 4. Content Extraction and Analysis

For each search result, the agent extracts and analyzes the content:

- It scrapes each URL with appropriate rate limiting (1-second delay between operations)
- For each scraped page, it analyzes the content for relevance to the original query
- The ContentAnalyzerTool breaks down long content into manageable chunks
- It scores content based on relevance (0-10 scale) and extracts the most relevant portions
- Only content with a relevance score of 5 or higher is retained
- Results are sorted by relevance score and limited to the configured maximum (max_extracted_sources)

### 5. Information Synthesis

Finally, the agent synthesizes the extracted information into a comprehensive report:

- It prepares the context by combining the most relevant content from top sources
- Each source's content is limited to the configured maximum length (max_synthesis_content_length)
- The agent uses the Gemini model to generate a concise report that answers the query
- It adds proper citations and source references to the final report
- If no relevant information is found, it provides appropriate feedback to the user

## Problem Handling

The WebResearchAgent incorporates robust error handling mechanisms to deal with various challenges that may arise during the research process:

### 1. Handling Unreachable Websites

When websites are unreachable or return errors:

- The WebScraperTool implements a 10-second timeout for all requests
- If a website fails to load, the agent returns an empty content object with an "Error loading page" title
- The agent continues processing other results rather than failing the entire operation
- This graceful degradation ensures the agent can still provide useful information even if some sources are unavailable

### 2. Managing API Failures

To handle API failures (search API, Gemini API):

- Each API call is wrapped in try-except blocks to catch and handle exceptions
- If the query analysis fails, the agent falls back to using the original query as the search term
- If JSON parsing fails, the agent implements fallback mechanisms to extract useful information
- Rate limiting is implemented to prevent API throttling (3-second minimum interval between API calls)

### 3. Dealing with Conflicting Information

When sources provide conflicting information:

- The agent scores content based on relevance and source quality (0-10 scale)
- Higher quality sources (determined by the ContentAnalyzerTool) are prioritized
- Educational sources (.edu domains) are given preference for complex topics
- News sources are evaluated based on recency and authority
- The synthesis prompt instructs the model to create a coherent report that reconciles differences
- The agent sorts extracted data by relevance score before synthesis
- All sources are cited with proper attribution, allowing users to evaluate the information themselves

### 4. Resource Constraint Management

To operate within the strict resource constraints (0.1 CPU, 512MB RAM):

- Memory usage is actively monitored using psutil
- Garbage collection is forced at strategic points to free memory
- Variables are explicitly deleted after use to reduce memory pressure
- Content length is strictly limited at multiple stages (scraping, analysis, synthesis)
- The agent uses a lighter model (gemini-1.5-flash) to reduce computational requirements

### 5. Handling Malformed or Empty Results

To prevent errors from malformed or empty data:

- Null checks are implemented throughout the codebase
- Default values are provided for missing fields
- Type checking ensures data is in the expected format
- Fallback mechanisms are implemented at each stage of the process

### 6. Rate Limiting and Throttling

To prevent CPU spikes and API throttling:

- The agent implements rate limiting between operations (1-3 seconds)
- Time delays are added between consecutive web scraping operations
- API calls are spaced out to prevent overloading external services
- The _rate_limit method ensures consistent pacing of operations

### 7. Timeout and Recovery

To handle long-running operations:

- Web scraping has a 10-second timeout to prevent hanging on slow websites
- Content analysis is chunked to process large documents efficiently
- If a step fails, the agent attempts to continue with partial results rather than failing completely

## Future Improvements

Potential areas for improvement include:
1. Adding support for more search engines
2. Implementing caching to improve performance
3. Adding user authentication
4. Improving the web interface with real-time updates
5. Adding support for file uploads and downloads
