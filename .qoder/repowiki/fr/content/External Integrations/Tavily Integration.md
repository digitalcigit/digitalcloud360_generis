# Tavily Integration

<cite>
**Referenced Files in This Document**   
- [tavily.py](file://app/core/integrations/tavily.py)
- [settings.py](file://app/config/settings.py)
- [research.py](file://app/core/agents/research.py)
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [TavilyClient Implementation](#tavilyclient-implementation)
3. [ResearchAgent Usage](#researchagent-usage)
4. [Error Handling Strategies](#error-handling-strategies)
5. [Configuration Options](#configuration-options)
6. [Data Privacy Considerations](#data-privacy-considerations)
7. [Troubleshooting Guide](#troubleshooting-guide)

## Introduction
The Tavily integration within the Genesis AI Deep Agents Service enables automated market research and competitor analysis for African entrepreneurs. This document details the implementation of the `TavilyClient` class, its integration with the `ResearchAgent`, and associated configuration, error handling, and privacy considerations. The system leverages the Tavily API to gather real-time market intelligence, which is then used to generate comprehensive business briefs.

## TavilyClient Implementation

The `TavilyClient` class serves as a wrapper around the Tavily SDK, providing specialized methods for market research in the African context. It handles API authentication, request construction, and response parsing.

### Authentication and Initialization
The client authenticates with the Tavily API using an API key retrieved from the application settings. During initialization, it validates the presence of the `TAVILY_API_KEY` environment variable.

```python
def __init__(self):
    if not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    self.client = TavilySDK(api_key=settings.TAVILY_API_KEY)
```

This ensures that the service fails fast if credentials are missing, preventing runtime errors during API calls.

### Search and Research Methods
The `TavilyClient` provides two primary methods for market intelligence gathering:

#### Market Search
The `search_market` method performs general market research by combining a query with a geographic location (default: "Africa").

**Parameters:**
- `query`: The search query string (e.g., "market trends")
- `location`: Geographic focus for the search (default: "Africa")

**Implementation:**
```python
async def search_market(self, query: str, location: str = "Africa") -> List[Dict[str, Any]]:
    try:
        search_query = f"{query} in {location}"
        logger.info("Performing market search with Tavily", query=search_query)
        response = await self.client.search(query=search_query, search_depth="advanced")
        logger.info("Successfully performed market search", query=search_query)
        return response['results']
    except Exception as e:
        logger.error("Tavily market search failed", query=query, location=location, error=str(e))
        return []
```

The method constructs a search query with location context, logs the operation, and returns the results. On failure, it returns an empty list as a fallback.

#### Competitor Analysis
The `analyze_competitors` method identifies and analyzes competitors within a specific business sector and location.

**Parameters:**
- `business_sector`: The industry or sector (e.g., "e-commerce")
- `location`: Geographic market of interest

**Implementation:**
```python
async def analyze_competitors(self, business_sector: str, location: str) -> Dict[str, Any]:
    try:
        query = f"competitors of {business_sector} in {location}"
        logger.info("Performing competitor analysis with Tavily", query=query)
        response = await self.client.search(query=query, search_depth="advanced")
        logger.info("Successfully performed competitor analysis", query=query)
        return {"analysis": response['results']}
    except Exception as e:
        logger.error(
            "Tavily competitor analysis failed", 
            business_sector=business_sector, 
            location=location, 
            error=str(e)
        )
        return {"error": "Failed to analyze competitors."}
```

This method returns a structured dictionary containing competitor analysis results or an error message on failure.

**Section sources**
- [tavily.py](file://app/core/integrations/tavily.py#L7-L43)

## ResearchAgent Usage

The `ResearchAgent` orchestrates market research by leveraging the `TavilyClient` to gather and synthesize market intelligence.

### Method Parameters
The `run` method accepts two key parameters:

- `company_description`: A textual description of the client's business
- `market_focus`: The target market (e.g., "e-commerce de mode au Sénégal")

### Workflow
The agent executes a two-step research process:

1. **Market Research**: Searches for general market analysis in Africa related to the market focus
2. **Competitor Analysis**: Identifies main competitors for the specified market focus

```python
async def run(self, company_description: str, market_focus: str) -> dict:
    try:
        # 1. Market research
        market_research = await self.tavily_client.search_market(
            query=f"Analyse du marché pour {market_focus} en Afrique",
            topic="market_analysis"
        )
        
        # 2. Competitor analysis
        competitor_analysis = await self.tavily_client.analyze_competitors(
            query=f"Concurrents principaux pour {market_focus}",
            company_description=company_description
        )
        
        return {
            "market_research": market_research,
            "competitor_analysis": competitor_analysis
        }
    except Exception as e:
        logger.error("Error during research agent execution", error=str(e))
        raise AgentException(
            "RESEARCH_AGENT_ERROR",
            "Failed to execute market research.",
            details=str(e)
        )
```

The agent returns a structured dictionary containing both market research and competitor analysis results, which are used downstream for business brief generation.

**Section sources**
- [research.py](file://app/core/agents/research.py#L6-L57)

## Error Handling Strategies

The Tavily integration implements robust error handling to ensure system reliability despite external API failures.

### Exception Handling
Both the `TavilyClient` and `ResearchAgent` use try-except blocks to catch and handle exceptions:

- **TavilyClient**: Returns fallback values (empty list or error dictionary) on failure, ensuring the calling agent can continue execution
- **ResearchAgent**: Propagates errors as `AgentException` with detailed error codes and messages, enabling proper error reporting to clients

### Logging
Comprehensive logging is implemented at key points:
- Informational logs for successful operations
- Error logs with contextual data (query, location, error message) for debugging

### Failure Modes
The system handles various failure scenarios:
- Missing API keys (validation at initialization)
- Network errors during API calls
- Service unavailability
- Unexpected response formats

The current implementation does not include retry logic or timeout handling specific to Tavily, unlike other integrations in the system.

## Configuration Options

The Tavily integration supports several configuration options through the application settings.

### API Key Configuration
The `TAVILY_API_KEY` setting in `settings.py` stores the authentication credential for the Tavily API.

### Base URL Override
The `TAVILY_BASE_URL` setting allows for base URL overrides, enabling:
- Testing against staging environments
- Custom deployment configurations
- API endpoint customization

```python
TAVILY_BASE_URL: str = "https://api.tavily.com"
```

### Configuration Structure
The settings are managed through Pydantic's `BaseSettings`, allowing configuration via:
- Environment variables
- `.env` files
- Default values

While timeout and retry configurations exist for other services (e.g., DigitalCloud360), similar settings for Tavily are not currently implemented in the codebase.

**Section sources**
- [settings.py](file://app/config/settings.py#L70-L83)
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py#L11-L14)

## Data Privacy Considerations

When sending user business ideas to Tavily, the following privacy considerations apply:

### Data Transmission
- Business descriptions and market focus queries are sent to Tavily's external API
- Data is transmitted over HTTPS with API key authentication
- No personally identifiable information (PII) is explicitly included in the queries

### Security Measures
- API keys are stored in environment variables and loaded securely via settings
- The system follows the principle of least privilege with API access
- All external API connections are validated at startup

### Privacy Recommendations
- Users should avoid including sensitive personal or financial information in business descriptions
- The system should implement data minimization, sending only necessary information to external APIs
- Consider implementing data anonymization for business descriptions before external transmission
- Review Tavily's data handling and privacy policies to ensure compliance with regional regulations (particularly for African markets)

The current implementation does not include explicit data sanitization or anonymization before sending requests to Tavily.

## Troubleshooting Guide

This section addresses common issues encountered with the Tavily integration.

### Invalid Credentials
**Symptom**: `ValueError: TAVILY_API_KEY is not set in the environment variables.`
**Solution**: 
1. Ensure the `TAVILY_API_KEY` is set in the environment or `.env` file
2. Verify the environment variables are loaded correctly
3. Restart the application after configuration changes

### Unexpected Response Formats
**Symptom**: Errors when parsing Tavily API responses
**Solution**:
1. Check Tavily API documentation for response schema changes
2. Implement response validation and schema checking
3. Add defensive programming to handle missing fields

### Service Unavailability
**Symptom**: Consistent failures in market research operations
**Solution**:
1. Verify Tavily API status
2. Check network connectivity
3. Implement retry logic with exponential backoff (currently not present in TavilyClient)
4. Consider implementing circuit breaker pattern

### Configuration Issues
**Symptom**: Connection to wrong API endpoint
**Solution**:
1. Verify `TAVILY_BASE_URL` setting
2. Ensure environment-specific configurations are correctly loaded
3. Check for typos in URL configuration

### Performance Issues
**Symptom**: Slow market research operations
**Recommendations**:
1. Implement caching of frequent queries
2. Add timeout configuration (currently not available)
3. Monitor API response times and set appropriate expectations

**Section sources**
- [tavily.py](file://app/core/integrations/tavily.py#L7-L43)
- [settings.py](file://app/config/settings.py#L70-L83)
- [research.py](file://app/core/agents/research.py#L6-L57)