from typing import List, Dict, Any
from langchain_core.graphs import StateGraph, END
from langgraph.graph import Graph
import asyncio
from models import (
    Query, SearchResult, BrandMention, MarketingInsight,
    BrandAnalysisResult
)
from llm_wrappers import OpenAIWrapper, PerplexityWrapper, QueryGenerator
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class BrandResearchPipeline:
    def __init__(self):
        self.openai_wrapper = OpenAIWrapper()
        self.perplexity_wrapper = PerplexityWrapper()
        self.query_generator = QueryGenerator()
        self.client = OpenAI()
        
    async def generate_queries(self, brand_name: str) -> List[Query]:
        """Generate simulated consumer queries"""
        raw_queries = await self.query_generator.generate_queries(brand_name)
        return [Query(**q) for q in raw_queries]
    
    async def search_with_llms(self, queries: List[Query]) -> List[SearchResult]:
        """Execute searches across multiple LLMs"""
        results = []
        for query in queries:
            # Run searches in parallel
            openai_task = self.openai_wrapper.search(query.text)
            perplexity_task = self.perplexity_wrapper.search(query.text)
            llm_results = await asyncio.gather(openai_task, perplexity_task)
            results.extend(llm_results)
        return results
    
    async def analyze_sources(
        self, 
        brand_name: str, 
        search_results: List[SearchResult]
    ) -> List[BrandMention]:
        """Analyze sources for brand mentions and context"""
        mentions = []
        
        # Combine all sources for analysis
        all_sources = []
        for result in search_results:
            all_sources.extend(result.sources)
        
        # Use OpenAI to analyze sources in batches
        batch_size = 5
        for i in range(0, len(all_sources), batch_size):
            batch = all_sources[i:i + batch_size]
            
            analysis_prompt = f"""
            Analyze these sources for mentions of {brand_name} and its competitors.
            For each source, identify:
            1. The context of brand mentions
            2. The sentiment (positive/negative/neutral)
            3. Any competitor brands mentioned
            
            Sources to analyze:
            {[{'url': s.url, 'content': s.snippet} for s in batch]}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            # Process the response to create BrandMention objects
            # This would need proper parsing of the response
            
        return mentions
    
    async def generate_insights(
        self,
        brand_mentions: List[BrandMention]
    ) -> List[MarketingInsight]:
        """Generate marketing insights from the analysis"""
        # Use GPT-4 to generate insights
        insights_prompt = f"""
        Based on the following brand mentions and analysis, generate key marketing insights.
        Categorize each insight and provide supporting evidence.
        
        Brand Mentions:
        {[m.dict() for m in brand_mentions]}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": insights_prompt}]
        )
        
        # Process the response to create MarketingInsight objects
        # This would need proper parsing of the response
        return []
    
    async def calculate_visibility_score(
        self,
        brand_mentions: List[BrandMention],
        search_results: List[SearchResult]
    ) -> float:
        """Calculate overall brand visibility score"""
        # Implement scoring logic based on:
        # - Frequency of brand mentions
        # - Quality of sources
        # - Sentiment distribution
        # - Competitor presence
        return 0.0
    
    async def generate_summary(
        self,
        brand_name: str,
        mentions: List[BrandMention],
        insights: List[MarketingInsight],
        visibility_score: float
    ) -> str:
        """Generate a markdown summary of the analysis"""
        summary_prompt = f"""
        Create a comprehensive markdown summary of the brand presence analysis for {brand_name}.
        Include:
        - Overall visibility score: {visibility_score}
        - Key findings
        - Important sources (with links)
        - Competitor analysis
        - Recommendations
        
        Data:
        Brand Mentions: {[m.dict() for m in mentions]}
        Marketing Insights: {[i.dict() for i in insights]}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        return response.choices[0].message.content
    
    def build_graph(self) -> Graph:
        """Build the LangGraph workflow"""
        
        # Define the graph
        workflow = StateGraph(nodes=["start"])
        
        # Add nodes for each step
        workflow.add_node("generate_queries", self.generate_queries)
        workflow.add_node("search_llms", self.search_with_llms)
        workflow.add_node("analyze_sources", self.analyze_sources)
        workflow.add_node("generate_insights", self.generate_insights)
        workflow.add_node("calculate_score", self.calculate_visibility_score)
        workflow.add_node("generate_summary", self.generate_summary)
        
        # Define edges
        workflow.add_edge("start", "generate_queries")
        workflow.add_edge("generate_queries", "search_llms")
        workflow.add_edge("search_llms", "analyze_sources")
        workflow.add_edge("analyze_sources", "generate_insights")
        workflow.add_edge("analyze_sources", "calculate_score")
        workflow.add_edge("generate_insights", "generate_summary")
        workflow.add_edge("calculate_score", "generate_summary")
        workflow.add_edge("generate_summary", END)
        
        return workflow.compile()
    
    async def run_analysis(self, brand_name: str) -> BrandAnalysisResult:
        """Run the complete brand analysis pipeline"""
        graph = self.build_graph()
        
        # Execute the graph
        result = await graph.ainvoke({
            "brand_name": brand_name,
            "state": {}
        })
        
        # Process results into final BrandAnalysisResult
        return BrandAnalysisResult(
            brand_name=brand_name,
            simulated_queries=result["queries"],
            search_results=result["search_results"],
            brand_mentions=result["mentions"],
            insights=result["insights"],
            visibility_score=result["visibility_score"],
            summary_markdown=result["summary"]
        )
