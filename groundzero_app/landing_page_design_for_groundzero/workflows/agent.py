from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from models import BrandAnalysisResult
from pipeline import BrandResearchPipeline
import json

# Create the main agent
brand_research_agent = Agent(
    name="brand_research_agent",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
    seed="brand_research_seed"
)

# Fund the agent if needed
fund_agent_if_low(brand_research_agent.wallet.address())

# Create the research protocol
research_protocol = Protocol("brand_research")

@research_protocol.on_message
async def handle_research_request(ctx: Context, sender: str, msg: dict):
    """Handle incoming brand research requests"""
    try:
        brand_name = msg.get("brand_name")
        if not brand_name:
            await ctx.send(sender, {
                "error": "Brand name is required"
            })
            return
            
        # Initialize the research pipeline
        pipeline = BrandResearchPipeline()
        
        # Run the analysis
        ctx.logger.info(f"Starting brand research for: {brand_name}")
        result = await pipeline.run_analysis(brand_name)
        
        # Send back the results
        await ctx.send(sender, {
            "status": "success",
            "result": json.dumps(result.dict())
        })
        
    except Exception as e:
        ctx.logger.error(f"Error processing request: {str(e)}")
        await ctx.send(sender, {
            "error": str(e)
        })

# Register the protocol with the agent
brand_research_agent.include(research_protocol)

if __name__ == "__main__":
    brand_research_agent.run()
