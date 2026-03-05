#!/usr/bin/env python3
"""
任务协作模块 - 完整实现

管理任务的完整生命周期，支持多Agent协作、依赖管理、子任务分解。
提供完整的任务工作流引擎，支持多种协作模式。
"""

from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import uuid
import json
from collections import defaultdict


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = auto()      # 待处理
    ASSIGNED = auto()     # 已分配
    IN_PROGRESS = auto()  # 进行中
    BLOCKED = auto()      # 被阻塞
    REVIEWING = auto()    # 审核中
    COMPLETED = auto()    # 已完成
    CANCELLED = auto()    # 已取消
    FAILED = auto()       # 失败


class TaskPriority(Enum):
    """任务优先级枚举"""
    CRITICAL = 5   # 紧急
    HIGH = 4       # 高
    MEDIUM = 3     # 中
    LOW = 2        # 低
    TRIVIAL = 1    # 微不足道


class TaskType(Enum):
    """任务类型枚举"""
    SINGLE = auto()       # 单任务
    COMPOSITE = auto()    # 复合任务（包含子任务）
    PARALLEL = auto()     # 并行任务
    SEQUENTIAL = auto() # 顺序任务


class CollaborationMode(Enum):
    """协作模式枚举"""
    COMPETITIVE = auto()  # 竞争模式（多个Agent竞争执行）
    COLLABORATIVE = auto() # 协作模式（多个Agent共同完成）
    PIPELINE = auto()     # 流水线模式（按顺序传递任务）


@dataclass
class TaskRequirement:
    """任务需求定义"""
    skill_id: Optional[str] = None           # 所需技能ID
    min_proficiency: float = 0.0             # 最低熟练度（0-1）
    capabilities: List[str] = field(default_factory=list)  # 所需能力列表
    tools: List[str] = field(default_factory=list)         # 所需工具列表
    resources: Dict[str, Any] = field(default_factory=dict) # 所需资源

@dataclass
class TaskOutput:
    """任务输出定义"""
    name: str                              # 输出名称
    type: str                              # 输出类型（string, number, object等）
    description: str = ""                  # 输出描述
    required: bool = True                  # 是否必需
    validation_rules: List[Dict] = field(default_factory=list)  # 验证规则

@dataclass
class TaskCollaborationInfo:
    """任务协作信息"""
    mode: CollaborationMode = CollaborationMode.COLLABORATIVE  # 协作模式
    participants: List[str] = field(default_factory=list)     # 参与者列表
    coordinator_id: Optional[str] = None                     # 协调者ID
    division_of_labor: Dict[str, str] = field(default_factory=dict)  # 分工
    shared_resources: List[str] = field(default_factory=list)  # 共享资源

@dataclass
class Task:
    """任务核心类 - 完整任务生命周期管理"""
    
    # ========== 基本信息 ==========
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    task_type: TaskType = TaskType.SINGLE
    
    # ========== 状态和优先级 ==========
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # ========== 时间信息 ==========
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # 估计时长（秒）
    actual_duration: Optional[int] = None     # 实际时长（秒）
    
    # ========== 人员和角色 ==========
    creator_id: Optional[str] = None
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)
    watchers: List[str] = field(default_factory=list)
    
    # ========== 任务内容和要求 ==========
    requirements: TaskRequirement = field(default_factory=TaskRequirement)
    outputs: List[TaskOutput] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # ========== 任务关系 ==========
    parent_id: Optional[str] = None                    # 父任务
    subtasks: List[str] = field(default_factory=list)  # 子任务
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务
    dependents: List[str] = field(default_factory=list)    # 依赖本任务的任务
    related_tasks: List[str] = field(default_factory=list) # 相关任务
    
    # ========== 协作信息 ==========
    collaboration: TaskCollaborationInfo = field(default_factory=TaskCollaborationInfo)
    
    # ========== 执行信息 ==========
    execution_count: int = 0          # 执行次数
    last_error: Optional[str] = None # 上次错误信息
    retry_count: int = 0             # 重试次数
    max_retries: int = 3             # 最大重试次数
    
    # ========== 标签和分类 ==========
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    project_id: Optional[str] = None
    
    # ========== 元数据 ==========
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # ========== 审计日志 ==========
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后的处理"""
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
    
    def update_status(self, new_status: TaskStatus, reason: Optional[str] = None) -> None:
        """更新任务状态"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        # 记录审计日志
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "status_change",
            "old_value": old_status.name if old_status else None,
            "new_value": new_status.name,
            "reason": reason,
        })
        
        # 更新开始/完成时间
        if new_status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = datetime.now()
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.FAILED]:
            self.completed_at = datetime.now()
            if self.started_at:
                self.actual_duration = int((self.completed_at - self.started_at).total_seconds())
    
    def assign_to(self, agent_id: str) -> None:
        """分配给指定Agent"""
        self.assignee_id = agent_id
        self.update_status(TaskStatus.ASSIGNED, f"Assigned to agent {agent_id}")
    
    def add_subtask(self, task_id: str) -> None:
        """添加子任务"""
        if task_id not in self.subtasks:
            self.subtasks.append(task_id)
    
    def add_dependency(self, task_id: str) -> None:
        """添加依赖任务"""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
    
    def check_dependencies_satisfied(self, all_tasks: Dict[str, "Task"]) -> bool:
        """检查所有依赖是否已完成"""
        for dep_id in self.dependencies:
            dep_task = all_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def add_comment(self, author_id: str, content: str) -> None:
        """添加评论"""
        self.comments.append({
            "comment_id": str(uuid.uuid4()),
            "author_id": author_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.name,
            "status": self.status.name,
            "priority": self.priority.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "creator_id": self.creator_id,
            "assignee_id": self.assignee_id,
            "reviewer_id": self.reviewer_id,
            "collaborators": self.collaborators,
            "watchers": self.watchers,
            "parent_id": self.parent_id,
            "subtasks": self.subtasks,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "related_tasks": self.related_tasks,
            "tags": self.tags,
            "category": self.category,
            "project_id": self.project_id,
            "metadata": self.metadata,
            "custom_fields": self.custom_fields,
            "audit_log_count": len(self.audit_log),
            "comments_count": len(self.comments),
            "attachments_count": len(self.attachments),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建"""
        task = cls(
            task_id=data.get("task_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
        )
        
        # 恢复其他字段
        if "task_type" in data:
            task.task_type = TaskType[data["task_type"]]
        if "status" in data:
            task.status = TaskStatus[data["status"]]
        if "priority" in data:
            task.priority = TaskPriority[data["priority"]]
        
        # 时间字段
        for field in ["created_at", "updated_at", "deadline", "started_at", "completed_at"]:
            if field in data and data[field]:
                setattr(task, field, datetime.fromisoformat(data[field]))
        
        # 其他字段
        for field in ["estimated_duration", "actual_duration", "creator_id", "assignee_id",
                     "reviewer_id", "collaborators", "watchers", "parent_id", "subtasks",
                     "dependencies", "dependents", "related_tasks", "tags", "category",
                     "project_id", "metadata", "custom_fields"]:
            if field in data:
                setattr(task, field, data[field])
        
        return task


# 导出类
__all__ = [
    'Task',
    'TaskStatus',
    'TaskPriority',
    'TaskType',
    'CollaborationMode',
    'TaskRequirement',
    'TaskOutput',
    'TaskCollaborationInfo'
]