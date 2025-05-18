"""
LLM Service module for brand presence analysis.
Centralizes LLM initialization to avoid circular imports.
"""
import os
import traceback
import yaml

from typing import Dict, Any, Optional, TypeVar
from datetime import datetime
from pydantic import BaseModel

from langchain_perplexity import ChatPerplexity

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage

import logging
# Initialize logger
logger = logging.getLogger("brand_zero.llm_service")

# Import models and utilities
from models import TransformationState, StepStatus, IntermediateStep
from utils import extract_json_from_text, CONFIG

T = TypeVar('T')

def get_llm(config: Dict[str, Any] = None) -> ChatPerplexity:
    """Get LLM model with Perplexity Sonar integration
    
    Args:
        config: Optional configuration dictionary. If None, loads from default config.
        model_name: Optional model name to override config.
        temperature: Optional temperature value to override config.
        max_tokens: Optional max_tokens value to override config.
        
    Returns:
        ChatPerplexity instance configured with provided parameters
        
    Raises:
        ValueError: If PERPLEXITY_API_KEY is not set in environment variables
    """
    # Check for API key
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        logger.error("PERPLEXITY_API_KEY environment variable must be set")
        raise ValueError("PERPLEXITY_API_KEY environment variable must be set")
    
    # Get model configuration from config
    # Handle both direct model config and nested model field
    if config and isinstance(config, dict) and "model" in config:
        model_config = config["model"]
    elif config:
        model_config = config.get("model", {})
    else:
        model_config = {}
    
    # Use provided parameters or fall back to config values
    model = model_config.get("name", "sonar-pro")
    temp = model_config.get("temperature", 0.7)
    tokens = model_config.get("max_tokens", 2000)
    
    logger.info(f"Initializing LLM with model={model}, temperature={temp}, max_tokens={tokens}")
    
    # Create and return the model
    try:
        return ChatPerplexity(
            model=model,
            temperature=temp,
            max_tokens=tokens,
            pplx_api_key=api_key
        )
    except Exception as e:
        logger.error(f"Error creating ChatPerplexity model: {str(e)}")
        raise ValueError(f"Failed to initialize ChatPerplexity model: {str(e)}")

# Singleton LLM instance
_llm_instance = None

def get_llm_instance(config: Dict[str, Any] = None) -> ChatPerplexity:
    """Get or create a singleton LLM instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ChatPerplexity instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_llm(config)
    return _llm_instance


async def create_analysis_step(
    state: Optional[TransformationState],
    step_name: str,
    prompt_key: str,
    input_variables: Dict[str, Any],
    parser: Optional[PydanticOutputParser[T]] = None,
    dependencies: Optional[Dict[str, str]] = None
) -> BaseModel:
    """Create an analysis step with common error handling and state management."""
    try:
        step = IntermediateStep(
            step_name=step_name,
            status=StepStatus.RUNNING,
            start_time=datetime.now(),
            input_data=input_variables
        )
        if state:
            state.intermediate_steps.append(step)

        # Check dependencies
        if dependencies:
            for dep_name, error_msg in dependencies.items():
                if not getattr(state, dep_name):
                    step.status = StepStatus.ERROR
                    step.end_time = datetime.now()
                    step.error = error_msg
                    if state:
                        state.error = error_msg
                    return None

        # Get system prompt
        system_prompt = CONFIG["prompts"].get("system", "")
        
        # Create prompt
        prompt = PromptTemplate(
            template=CONFIG["prompts"][prompt_key],
            input_variables=list(input_variables.keys())
        )
        if parser:
            input_variables.update({
                "format_instructions": parser.get_format_instructions()
            })
        
        # Format prompt with input variables
        formatted_prompt = prompt.format(**input_variables)
        
        # Get LLM response with system prompt
        try:
            # Combine system prompt and formatted prompt
            full_prompt = f"{system_prompt}\n\n{formatted_prompt}" if system_prompt else formatted_prompt
            
            # Call the LLM
            response = await get_llm_instance(CONFIG).ainvoke(full_prompt)
            
            # Extract content from AIMessage if needed
            llm_output = response.content if isinstance(response, AIMessage) else response
            
            # Parse response if parser provided
            if parser:
                try:
                    # First try normal parsing
                    result: T = parser.parse(llm_output)
                except Exception as parse_error:
                    logger.error(f"Error parsing LLM output: {parse_error}")
                    logger.error(f"Raw output: {llm_output}")
                    # Try fallback JSON extraction
                    logger.info("Attempting fallback JSON extraction")
                    json_data, raw_text = extract_json_from_text(llm_output)
                    # Store raw text in state context if available
                    if state and raw_text:
                        if step_name not in state.context:
                            state.context[step_name] = []
                        state.context[step_name].append(raw_text)
                        logger.info(f"Appended raw text to context for step: {step_name}")
                    if json_data is not None:
                        logger.info(f"Successfully extracted JSON data using fallback method")
                        try:
                            model_class: T = parser.pydantic_object
                            # If the model expects a 'queries' field and json_data is a list, wrap it
                            if hasattr(model_class, 'model_fields') and 'queries' in getattr(model_class, 'model_fields', {}):
                                if isinstance(json_data, list):
                                    json_data = {"queries": json_data}
                            result = model_class(**json_data)
                            logger.info(f"Successfully created {model_class.__name__} from extracted JSON")
                        except Exception as model_error:
                            logger.error(f"Error creating model from extracted JSON: {model_error}. Returning extracted JSON as dict due to model creation error")
                            logger.error(f"Model class: {model_class}")
                            logger.error(f"Extracted json_data: {json_data}")
                            result = json_data
                    else:
                        logger.error("Failed to extract JSON using fallback method")
                        step.status = StepStatus.ERROR
                        step.end_time = datetime.now()
                        step.error = f"Error parsing LLM output: {str(parse_error)}. Fallback extraction also failed."
                        return None
            else:
                result = llm_output
                
                # Store raw LLM output in state context if no parser was used
                if state:
                    if step_name not in state.context:
                        state.context[step_name] = []
                    state.context[step_name].append(llm_output)
                    logger.info(f"Appended raw LLM output to context for step: {step_name}")
        except Exception as llm_error:
            logger.error(f"Error calling LLM: {str(llm_error)}")
            step.status = StepStatus.ERROR
            step.end_time = datetime.now()
            step.error = f"Error calling LLM: {str(llm_error)}"
            return None

        # Update step status
        step.status = StepStatus.COMPLETED
        step.end_time = datetime.now()
        step.output_data = result.dict() if hasattr(result, 'dict') else result

        return result

    except Exception as e:
        logger.error(f"Error in {step_name}: {str(e)}")
        logger.error(traceback.format_exc())
        step.status = StepStatus.ERROR
        step.end_time = datetime.now()
        step.error = str(e)
        if state:
            state.error = f"Error in {step_name}: {str(e)}"
        return None