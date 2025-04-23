# WebResearchAgent: Decision-Making Process and Problem Handling

## How the Agent Makes Decisions

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

## How the Agent Handles Problems

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

By implementing these robust decision-making and problem-handling mechanisms, the WebResearchAgent can reliably perform web research tasks even in resource-constrained environments and when facing various challenges like unreachable websites, API failures, or conflicting information.
