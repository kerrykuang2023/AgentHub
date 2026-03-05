"""
Agent 核心模块

定义 Agent 的身份、能力、状态和行为。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AgentCapability:
    """Agent 能力定义"""
    skill_id: str
    name: str
    proficiency_level: float = 0.0  # 0.0 - 1.0
    learning_source: Optional[str] = None
    acquired_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    usage_count: int = 0


@dataclass
class AgentIdentity:
    """Agent 身份定义"""
    agent_id: str
    name: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "0.1.0"
    

@dataclass
class AgentSocial:
    """Agent 社交属性"""
    reputation_score: float = 0.0
    contribution_points: int = 0
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)


@dataclass
class AgentLearningProfile:
    """Agent 学习偏好"""
    preferred_learning_style: str = "mixed"  # observation, practice, teaching, mixed
    active_learning_topics: List[str] = field(default_factory=list)
    learning_speed: float = 1.0  # 学习速度系数
    retention_rate: float = 0.8  # 知识留存率


class Agent:
    """
    Agent 核心类
    
    代表社区中的一个 AI Agent，包含身份、能力、状态和行为。
    """
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        creator: Optional[str] = None,
        avatar: Optional[str] = None,
        agent_id: Optional[str] = None,
    ):
        # 初始化身份
        self.identity = AgentIdentity(
            agent_id=agent_id or str(uuid.uuid4()),
            name=name,
            description=description,
            creator=creator,
            avatar=avatar,
        )
        
        # 初始化能力列表
        self.capabilities: Dict[str, AgentCapability] = {}
        
        # 初始化社交属性
        self.social = AgentSocial()
        
        # 初始化学习偏好
        self.learning_profile = AgentLearningProfile()
        
        # 状态
        self.status = "idle"  # idle, learning, working, collaborating
        self.current_task: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        
    def add_capability(self, capability: AgentCapability) -> None:
        """添加能力"""
        self.capabilities[capability.skill_id] = capability
        
    def remove_capability(self, skill_id: str) -> None:
        """移除能力"""
        if skill_id in self.capabilities:
            del self.capabilities[skill_id]
            
    def has_capability(self, skill_id: str, min_proficiency: float = 0.0) -> bool:
        """检查是否具备某能力"""
        if skill_id not in self.capabilities:
            return False
        return self.capabilities[skill_id].proficiency_level >= min_proficiency
    
    def update_reputation(self, delta: float) -> None:
        """更新声誉分数"""
        self.social.reputation_score = max(0, self.social.reputation_score + delta)
        
    def add_contribution_points(self, points: int) -> None:
        """增加贡献积分"""
        self.social.contribution_points += points
        
    def follow(self, agent_id: str) -> None:
        """关注其他 Agent"""
        if agent_id not in self.social.following:
            self.social.following.append(agent_id)
            
    def unfollow(self, agent_id: str) -> None:
        """取消关注"""
        if agent_id in self.social.following:
            self.social.following.remove(agent_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "identity": {
                "agent_id": self.identity.agent_id,
                "name": self.identity.name,
                "description": self.identity.description,
                "creator": self.identity.creator,
                "created_at": self.identity.created_at.isoformat(),
                "version": self.identity.version,
            },
            "capabilities": {
                skill_id: {
                    "skill_id": cap.skill_id,
                    "name": cap.name,
                    "proficiency_level": cap.proficiency_level,
                    "acquired_at": cap.acquired_at.isoformat(),
                    "usage_count": cap.usage_count,
                }
                for skill_id, cap in self.capabilities.items()
            },
            "social": {
                "reputation_score": self.social.reputation_score,
                "contribution_points": self.social.contribution_points,
                "followers_count": len(self.social.followers),
                "following_count": len(self.social.following),
                "achievements": self.social.achievements,
            },
            "status": self.status,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """从字典创建"""
        identity_data = data["identity"]
        agent = cls(
            name=identity_data["name"],
            description=identity_data.get("description"),
            creator=identity_data.get("creator"),
            agent_id=identity_data["agent_id"],
        )
        
        # 恢复能力
        for skill_data in data.get("capabilities", {}).values():
            cap = AgentCapability(
                skill_id=skill_data["skill_id"],
                name=skill_data["name"],
                proficiency_level=skill_data.get("proficiency_level", 0),
            )
            cap.usage_count = skill_data.get("usage_count", 0)
            agent.add_capability(cap)
        
        # 恢复社交数据
        social_data = data.get("social", {})
        agent.social.reputation_score = social_data.get("reputation_score", 0)
        agent.social.contribution_points = social_data.get("contribution_points", 0)
        agent.social.achievements = social_data.get("achievements", [])
        
        agent.status = data.get("status", "idle")
        agent.metadata = data.get("metadata", {})
        
        return agent
