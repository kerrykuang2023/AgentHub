"""
学习引擎模块

实现各种学习方式，让 Agent 能够自主学习新技能。
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class LearningStyle(Enum):
    """学习风格"""
    OBSERVATION = "observation"  # 观察学习
    INTERACTION = "interaction"  # 交互学习
    PRACTICE = "practice"       # 实践学习
    TRANSFER = "transfer"       # 迁移学习
    COLLABORATION = "collaboration"  # 协作学习
    MIXED = "mixed"            # 混合学习


class LearningStatus(Enum):
    """学习状态"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LearningObjective:
    """学习目标"""
    objective_id: str
    description: str
    skill_id: Optional[str] = None
    target_proficiency: float = 0.8  # 目标熟练度
    deadline: Optional[datetime] = None
    priority: int = 5  # 1-10，数字越大优先级越高
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningSession:
    """学习会话"""
    session_id: str
    learning_objective_id: str
    learning_style: LearningStyle
    status: LearningStatus = LearningStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    progress_percentage: float = 0.0
    notes: List[str] = field(default_factory=list)
    resources_used: List[str] = field(default_factory=list)


@dataclass
class LearningRecord:
    """学习记录"""
    record_id: str
    skill_id: str
    learning_style: LearningStyle
    start_time: datetime
    end_time: Optional[datetime] = None
    proficiency_before: float = 0.0
    proficiency_after: float = 0.0
    success: bool = False
    feedback: Optional[str] = None
    source_agent_id: Optional[str] = None  # 如果是从其他Agent学习


class LearningEngine:
    """
    学习引擎
    
    管理Agent的学习过程，支持多种学习方式。
    """
    
    def __init__(self, agent):
        """
        初始化学习引擎
        
        Args:
            agent: 关联的Agent实例
        """
        self.agent = agent
        
        # 学习目标
        self.objectives: Dict[str, LearningObjective] = {}
        
        # 学习会话
        self.active_sessions: Dict[str, LearningSession] = {}
        self.session_history: List[LearningSession] = []
        
        # 学习记录
        self.learning_records: List[LearningRecord] = []
        
        # 学习偏好（从Agent获取）
        self.preferred_style = agent.learning_profile.preferred_learning_style
        
        # 学习处理器
        self._learning_handlers = {
            LearningStyle.OBSERVATION: self._handle_observation_learning,
            LearningStyle.INTERACTION: self._handle_interaction_learning,
            LearningStyle.PRACTICE: self._handle_practice_learning,
            LearningStyle.TRANSFER: self._handle_transfer_learning,
            LearningStyle.COLLABORATION: self._handle_collaboration_learning,
        }
        
    def set_objective(self, objective: LearningObjective) -> None:
        """设置学习目标"""
        self.objectives[objective.objective_id] = objective
        
    def remove_objective(self, objective_id: str) -> None:
        """移除学习目标"""
        if objective_id in self.objectives:
            del self.objectives[objective_id]
            
    def start_learning_session(
        self,
        objective_id: str,
        learning_style: Optional[LearningStyle] = None,
    ) -> LearningSession:
        """
        开始学习会话
        
        Args:
            objective_id: 学习目标ID
            learning_style: 学习方式，默认使用Agent偏好
            
        Returns:
            LearningSession: 学习会话对象
        """
        if objective_id not in self.objectives:
            raise ValueError(f"Learning objective {objective_id} not found")
        
        # 确定学习方式
        style = learning_style or self.preferred_style or LearningStyle.MIXED
        
        # 创建会话
        import uuid
        session = LearningSession(
            session_id=str(uuid.uuid4()),
            learning_objective_id=objective_id,
            learning_style=style,
            status=LearningStatus.IN_PROGRESS,
            start_time=datetime.now(),
        )
        
        self.active_sessions[session.session_id] = session
        
        return session
        
    def end_learning_session(
        self,
        session_id: str,
        success: bool = True,
        notes: Optional[str] = None,
    ) -> LearningRecord:
        """
        结束学习会话
        
        Args:
            session_id: 会话ID
            success: 是否成功
            notes: 备注
            
        Returns:
            LearningRecord: 学习记录
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.status = LearningStatus.COMPLETED if success else LearningStatus.FAILED
        
        if notes:
            session.notes.append(notes)
        
        # 计算持续时间
        if session.start_time and session.end_time:
            session.duration_seconds = int(
                (session.end_time - session.start_time).total_seconds()
            )
        
        # 创建学习记录
        objective = self.objectives.get(session.learning_objective_id)
        record = LearningRecord(
            record_id=session_id,
            skill_id=objective.skill_id if objective else "unknown",
            learning_style=session.learning_style,
            start_time=session.start_time or datetime.now(),
            end_time=session.end_time,
            success=success,
            feedback=notes,
        )
        
        self.learning_records.append(record)
        
        # 移动到历史会话
        del self.active_sessions[session_id]
        self.session_history.append(session)
        
        return record
        
    def _handle_observation_learning(self, session: LearningSession, **kwargs) -> None:
        """处理观察学习"""
        # TODO: 实现观察学习逻辑
        session.notes.append("Observation learning not yet implemented")
        
    def _handle_interaction_learning(self, session: LearningSession, **kwargs) -> None:
        """处理交互学习"""
        # TODO: 实现交互学习逻辑
        session.notes.append("Interaction learning not yet implemented")
        
    def _handle_practice_learning(self, session: LearningSession, **kwargs) -> None:
        """处理实践学习"""
        # TODO: 实现实践学习逻辑
        session.notes.append("Practice learning not yet implemented")
        
    def _handle_transfer_learning(self, session: LearningSession, **kwargs) -> None:
        """处理迁移学习"""
        # TODO: 实现迁移学习逻辑
        session.notes.append("Transfer learning not yet implemented")
        
    def _handle_collaboration_learning(self, session: LearningSession, **kwargs) -> None:
        """处理协作学习"""
        # TODO: 实现协作学习逻辑
        session.notes.append("Collaboration learning not yet implemented")
        
    def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        total_sessions = len(self.session_history) + len(self.active_sessions)
        completed_sessions = len([s for s in self.session_history if s.status == LearningStatus.COMPLETED])
        failed_sessions = len([s for s in self.session_history if s.status == LearningStatus.FAILED])
        
        total_duration = sum(s.duration_seconds for s in self.session_history)
        
        # 按学习方式统计
        style_counts = {}
        for session in self.session_history:
            style = session.learning_style.value
            style_counts[style] = style_counts.get(style, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": completed_sessions,
            "failed_sessions": failed_sessions,
            "success_rate": completed_sessions / len(self.session_history) if self.session_history else 0,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": total_duration / len(self.session_history) if self.session_history else 0,
            "learning_style_distribution": style_counts,
            "total_objectives": len(self.objectives),
        }
