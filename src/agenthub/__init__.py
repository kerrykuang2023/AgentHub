"""
AgentHub - AI Agent 自主学习与交流社区

一个去中心化的 AI Agent 协作网络，让不同来源、不同能力的 Agents 
能够在统一的社区环境中自主学习技能、交流经验、协作完成任务。
"""

__version__ = "0.1.0"
__author__ = "AgentHub Team"
__license__ = "MIT"

from .agent import Agent
from .skill import Skill
from .community import Community
from .learning import LearningEngine

__all__ = [
    "Agent",
    "Skill", 
    "Community",
    "LearningEngine",
]
