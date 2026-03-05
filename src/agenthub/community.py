"""
社区模块

管理Agent之间的交流、社交和协作。
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class MessageType(Enum):
    """消息类型"""
    DIRECT = "direct"           # 私信
    GROUP = "group"             # 群组消息
    BROADCAST = "broadcast"     # 广播
    SYSTEM = "system"           # 系统通知
    SKILL_SHARE = "skill_share" # 技能分享
    TASK_ASSIGN = "task_assign" # 任务分配
    KNOWLEDGE_QUERY = "knowledge_query" # 知识查询


class ChannelType(Enum):
    """频道类型"""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    FORUM = "forum"
    WHITEBOARD = "whiteboard"
    CODE = "code"


@dataclass
class Message:
    """消息"""
    message_id: str
    sender_id: str
    recipient_id: str  # 可以是用户ID或频道ID
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None  # 回复的消息ID
    edit_history: List[Dict[str, Any]] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def edit(self, new_content: Dict[str, Any]) -> None:
        """编辑消息"""
        self.edit_history.append({
            "content": self.content,
            "timestamp": datetime.now().isoformat(),
        })
        self.content = new_content
        
    def add_reaction(self, emoji: str, user_id: str) -> None:
        """添加反应"""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        if user_id not in self.reactions[emoji]:
            self.reactions[emoji].append(user_id)
            
    def remove_reaction(self, emoji: str, user_id: str) -> None:
        """移除反应"""
        if emoji in self.reactions and user_id in self.reactions[emoji]:
            self.reactions[emoji].remove(user_id)


@dataclass
class Channel:
    """频道（群组/聊天室）"""
    channel_id: str
    name: str
    description: str
    channel_type: ChannelType
    creator_id: str
    created_at: datetime = field(default_factory=datetime.now)
    members: List[str] = field(default_factory=list)
    moderators: List[str] = field(default_factory=list)
    is_public: bool = False
    archived: bool = False
    pinned_messages: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_member(self, agent_id: str) -> None:
        """添加成员"""
        if agent_id not in self.members:
            self.members.append(agent_id)
            
    def remove_member(self, agent_id: str) -> None:
        """移除成员"""
        if agent_id in self.members:
            self.members.remove(agent_id)
        if agent_id in self.moderators:
            self.moderators.remove(agent_id)
            
    def add_moderator(self, agent_id: str) -> None:
        """添加管理员"""
        if agent_id in self.members and agent_id not in self.moderators:
            self.moderators.append(agent_id)
            
    def pin_message(self, message_id: str) -> None:
        """置顶消息"""
        if message_id not in self.pinned_messages:
            self.pinned_messages.append(message_id)
            
    def unpin_message(self, message_id: str) -> None:
        """取消置顶"""
        if message_id in self.pinned_messages:
            self.pinned_messages.remove(message_id)


class Community:
    """
    社区管理器
    
    管理所有Agent之间的交流、社交和协作。
    """
    
    def __init__(self):
        # 消息存储
        self._messages: Dict[str, Message] = {}
        self._user_messages: Dict[str, List[str]] = {}  # user_id -> message_ids
        self._channel_messages: Dict[str, List[str]] = {}  # channel_id -> message_ids
        
        # 频道存储
        self._channels: Dict[str, Channel] = {}
        
        # 社交关系
        self._followers: Dict[str, List[str]] = {}  # user_id -> followers
        self._following: Dict[str, List[str]] = {}  # user_id -> following
        
        # 在线状态
        self._online_status: Dict[str, Dict[str, Any]] = {}  # user_id -> status_info
        
        # 消息处理器
        self._message_handlers: List[Callable] = []
        
    # ========== 消息操作 ==========
    
    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        parent_id: Optional[str] = None,
    ) -> Message:
        """
        发送消息
        
        Args:
            sender_id: 发送者ID
            recipient_id: 接收者ID（用户ID或频道ID）
            message_type: 消息类型
            content: 消息内容
            parent_id: 回复的消息ID
            
        Returns:
            Message: 创建的消息对象
        """
        # 创建消息
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            parent_id=parent_id,
        )
        
        # 存储消息
        self._messages[message.message_id] = message
        
        # 更新用户消息索引
        if sender_id not in self._user_messages:
            self._user_messages[sender_id] = []
        self._user_messages[sender_id].append(message.message_id)
        
        # 如果是发给用户的私信
        if message_type == MessageType.DIRECT:
            if recipient_id not in self._user_messages:
                self._user_messages[recipient_id] = []
            self._user_messages[recipient_id].append(message.message_id)
        
        # 如果是频道消息
        if message_type in [MessageType.GROUP, MessageType.BROADCAST]:
            if recipient_id not in self._channel_messages:
                self._channel_messages[recipient_id] = []
            self._channel_messages[recipient_id].append(message.message_id)
        
        # 触发消息处理器
        for handler in self._message_handlers:
            try:
                handler(message)
            except Exception as e:
                # 记录错误但不中断
                print(f"Message handler error: {e}")
        
        return message
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """获取消息"""
        return self._messages.get(message_id)
    
    def get_user_messages(
        self,
        user_id: str,
        message_type: Optional[MessageType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """获取用户的消息"""
        message_ids = self._user_messages.get(user_id, [])
        messages = [self._messages[mid] for mid in message_ids if mid in self._messages]
        
        # 过滤消息类型
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        # 按时间倒序排序
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        
        # 分页
        return messages[offset:offset + limit]
    
    # ========== 频道操作 ==========
    
    def create_channel(
        self,
        name: str,
        description: str,
        channel_type: ChannelType,
        creator_id: str,
        is_public: bool = False,
    ) -> Channel:
        """创建频道"""
        channel = Channel(
            channel_id=str(uuid.uuid4()),
            name=name,
            description=description,
            channel_type=channel_type,
            creator_id=creator_id,
            is_public=is_public,
        )
        
        # 创建者自动成为成员和管理员
        channel.add_member(creator_id)
        channel.add_moderator(creator_id)
        
        self._channels[channel.channel_id] = channel
        
        return channel
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """获取频道"""
        return self._channels.get(channel_id)
    
    def join_channel(self, channel_id: str, agent_id: str) -> bool:
        """加入频道"""
        channel = self._channels.get(channel_id)
        if not channel:
            return False
        
        if channel.is_public or agent_id == channel.creator_id:
            channel.add_member(agent_id)
            return True
        
        # 私密频道需要邀请
        return False
    
    def leave_channel(self, channel_id: str, agent_id: str) -> bool:
        """离开频道"""
        channel = self._channels.get(channel_id)
        if not channel:
            return False
        
        channel.remove_member(agent_id)
        return True
    
    # ========== 社交功能 ==========
    
    def follow(self, follower_id: str, followee_id: str) -> bool:
        """关注"""
        if follower_id == followee_id:
            return False
        
        # 更新关注者的关注列表
        if follower_id not in self._following:
            self._following[follower_id] = []
        if followee_id not in self._following[follower_id]:
            self._following[follower_id].append(followee_id)
        
        # 更新被关注者的粉丝列表
        if followee_id not in self._followers:
            self._followers[followee_id] = []
        if follower_id not in self._followers[followee_id]:
            self._followers[followee_id].append(follower_id)
        
        return True
    
    def unfollow(self, follower_id: str, followee_id: str) -> bool:
        """取消关注"""
        # 从关注者的关注列表移除
        if follower_id in self._following and followee_id in self._following[follower_id]:
            self._following[follower_id].remove(followee_id)
        
        # 从被关注者的粉丝列表移除
        if followee_id in self._followers and follower_id in self._followers[followee_id]:
            self._followers[followee_id].remove(follower_id)
        
        return True
    
    def get_followers(self, agent_id: str) -> List[str]:
        """获取粉丝列表"""
        return self._followers.get(agent_id, [])
    
    def get_following(self, agent_id: str) -> List[str]:
        """获取关注列表"""
        return self._following.get(agent_id, [])
    
    # ========== 在线状态 ==========
    
    def set_online_status(self, agent_id: str, status: str, details: Optional[Dict] = None) -> None:
        """设置在线状态"""
        self._online_status[agent_id] = {
            "status": status,  # online, away, busy, offline
            "last_seen": datetime.now().isoformat(),
            "details": details or {},
        }
    
    def get_online_status(self, agent_id: str) -> Optional[Dict]:
        """获取在线状态"""
        return self._online_status.get(agent_id)
    
    # ========== 消息处理器 ==========
    
    def add_message_handler(self, handler: Callable[[Message], None]) -> None:
        """添加消息处理器"""
        self._message_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable[[Message], None]) -> None:
        """移除消息处理器"""
        if handler in self._message_handlers:
            self._message_handlers.remove(handler)
    
    # ========== 统计信息 ==========
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取社区统计信息"""
        return {
            "total_messages": len(self._messages),
            "total_channels": len(self._channels),
            "active_users": len(self._online_status),
            "online_users": len([u for u in self._online_status.values() if u.get("status") == "online"]),
        }
