"""
Skill / Persona model for assessment.
Defines the role, focus, and system prompts for the AI agent.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g. 'iso-auditor')")
    name: str = Field(..., description="Display name (e.g. 'ISO 27001 Lead Auditor')")
    description: str = Field(..., description="Short description of the role")
    system_prompt: str = Field(
        ..., description="Base system prompt defining the persona and constraints"
    )
    risk_focus: list[str] = Field(
        default_factory=list, description="Key areas to focus on (e.g. 'Access Control')"
    )
    compliance_frameworks: list[str] = Field(
        default_factory=list, description="Frameworks to reference (e.g. 'ISO 27001')"
    )
    is_builtin: bool = Field(default=False, description="Whether this is a system preset")


class SkillCreate(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    risk_focus: list[str] = []
    compliance_frameworks: list[str] = []


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    risk_focus: Optional[list[str]] = None
    compliance_frameworks: Optional[list[str]] = None
