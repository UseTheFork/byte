from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    model: str = Field(default="", description="The model identifier to use")
    provider: str = Field(default="", description="The models provider to use")
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    ask_agent_node: LLMModelConfig = LLMModelConfig()
    coder_agent_node: LLMModelConfig = LLMModelConfig()
    skill_creator_agent_node: LLMModelConfig = LLMModelConfig()
    coder_plan_agent_node: LLMModelConfig = LLMModelConfig()
    commit_agent_node: LLMModelConfig = LLMModelConfig()
    constitution_agent_node: LLMModelConfig = LLMModelConfig()
    skill_select_agent_node: LLMModelConfig = LLMModelConfig()
    spec_creator_agent_node: LLMModelConfig = LLMModelConfig()
