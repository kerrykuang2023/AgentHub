"""
安全与治理模块

管理Agent的身份验证、权限控制和治理机制。
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import hashlib
import secrets
import uuid


class PermissionLevel(Enum):
    """权限级别"""
    NONE = 0          # 无权限
    READ = 1          # 只读
    WRITE = 2         # 读写
    EXECUTE = 3       # 执行
    ADMIN = 4         # 管理
    OWNER = 5         # 所有者


class AuthMethod(Enum):
    """认证方式"""
    API_KEY = auto()      # API密钥
    TOKEN = auto()        # 令牌
    CERTIFICATE = auto()  # 证书
    BIOMETRIC = auto()    # 生物识别
    MFA = auto()          # 多因素认证


@dataclass
class Credential:
    """凭据"""
    credential_id: str
    agent_id: str
    auth_method: AuthMethod
    secret_hash: str  # 哈希后的密钥
    salt: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Permission:
    """权限"""
    resource_type: str  # 资源类型（task, skill, agent等）
    resource_id: Optional[str]  # 具体资源ID，None表示所有
    level: PermissionLevel
    granted_by: str  # 授权者
    granted_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class SecurityPolicy:
    """安全策略"""
    policy_id: str
    name: str
    description: str
    
    # 密码策略
    min_password_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    password_expiry_days: int = 90
    password_history_size: int = 5
    
    # 认证策略
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_mfa: bool = False
    session_timeout_minutes: int = 60
    
    # 审计策略
    log_all_actions: bool = True
    audit_retention_days: int = 365
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


class SecurityManager:
    """
    安全管理器
    
    管理认证、授权、加密和审计。
    """
    
    def __init__(self):
        # 凭据存储
        self._credentials: Dict[str, Credential] = {}  # credential_id -> Credential
        self._agent_credentials: Dict[str, List[str]] = {}  # agent_id -> credential_ids
        
        # 权限存储
        self._permissions: Dict[str, List[Permission]] = {}  # agent_id -> Permissions
        
        # 会话管理
        self._sessions: Dict[str, Dict[str, Any]] = {}  # session_token -> session_data
        self._session_expiry: Dict[str, datetime] = {}  # session_token -> expiry_time
        
        # 安全策略
        self._policies: Dict[str, SecurityPolicy] = {}
        self._default_policy: Optional[str] = None
        
        # 审计日志
        self._audit_log: List[Dict[str, Any]] = []
        
        # 登录失败记录
        self._failed_attempts: Dict[str, List[datetime]] = {}  # agent_id -> list of failed attempt times
        self._locked_accounts: Dict[str, datetime] = {}  # agent_id -> lock expiry time
    
    # ========== 凭据管理 ==========
    
    def create_credential(
        self,
        agent_id: str,
        auth_method: AuthMethod,
        secret: str,
        expires_in_days: Optional[int] = None,
    ) -> Credential:
        """创建新凭据"""
        # 生成盐值
        salt = secrets.token_hex(32)
        
        # 哈希密钥
        secret_hash = self._hash_secret(secret, salt)
        
        # 创建凭据
        credential = Credential(
            credential_id=str(uuid.uuid4()),
            agent_id=agent_id,
            auth_method=auth_method,
            secret_hash=secret_hash,
            salt=salt,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_in_days) if expires_in_days else None,
        )
        
        # 存储凭据
        self._credentials[credential.credential_id] = credential
        
        # 更新Agent的凭据列表
        if agent_id not in self._agent_credentials:
            self._agent_credentials[agent_id] = []
        self._agent_credentials[agent_id].append(credential.credential_id)
        
        # 记录审计日志
        self._log_audit_event("credential_created", agent_id, {"credential_id": credential.credential_id})
        
        return credential
    
    def verify_credential(self, credential_id: str, secret: str) -> bool:
        """验证凭据"""
        credential = self._credentials.get(credential_id)
        if not credential or not credential.is_active:
            return False
        
        # 检查是否过期
        if credential.expires_at and datetime.now() > credential.expires_at:
            return False
        
        # 验证密钥
        secret_hash = self._hash_secret(secret, credential.salt)
        if secret_hash != credential.secret_hash:
            return False
        
        # 更新最后使用时间
        credential.last_used_at = datetime.now()
        
        return True
    
    def revoke_credential(self, credential_id: str) -> bool:
        """撤销凭据"""
        credential = self._credentials.get(credential_id)
        if not credential:
            return False
        
        credential.is_active = False
        
        # 记录审计日志
        self._log_audit_event("credential_revoked", credential.agent_id, {"credential_id": credential_id})
        
        return True
    
    # ========== 权限管理 ==========
    
    def grant_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_id: Optional[str],
        level: PermissionLevel,
        granted_by: str,
        expires_at: Optional[datetime] = None,
    ) -> Permission:
        """授予权限"""
        permission = Permission(
            resource_type=resource_type,
            resource_id=resource_id,
            level=level,
            granted_by=granted_by,
            granted_at=datetime.now(),
            expires_at=expires_at,
        )
        
        # 添加到Agent的权限列表
        if agent_id not in self._permissions:
            self._permissions[agent_id] = []
        self._permissions[agent_id].append(permission)
        
        # 记录审计日志
        self._log_audit_event("permission_granted", agent_id, {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "level": level.name,
        })
        
        return permission
    
    def check_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_id: Optional[str],
        required_level: PermissionLevel,
    ) -> bool:
        """检查权限"""
        permissions = self._permissions.get(agent_id, [])
        
        for perm in permissions:
            # 检查资源类型匹配
            if perm.resource_type != resource_type:
                continue
            
            # 检查资源ID匹配（None表示匹配所有）
            if perm.resource_id is not None and perm.resource_id != resource_id:
                continue
            
            # 检查权限级别
            if perm.level.value < required_level.value:
                continue
            
            # 检查是否过期
            if perm.expires_at and datetime.now() > perm.expires_at:
                continue
            
            return True
        
        return False
    
    def revoke_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_id: Optional[str],
    ) -> bool:
        """撤销权限"""
        permissions = self._permissions.get(agent_id, [])
        
        for i, perm in enumerate(permissions):
            if perm.resource_type == resource_type and perm.resource_id == resource_id:
                del permissions[i]
                
                # 记录审计日志
                self._log_audit_event("permission_revoked", agent_id, {
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                })
                
                return True
        
        return False
    
    # ========== 会话管理 ==========
    
    def create_session(
        self,
        agent_id: str,
        credential_id: str,
        expires_in_minutes: int = 60,
    ) -> str:
        """创建会话"""
        # 生成会话令牌
        session_token = secrets.token_urlsafe(32)
        
        # 创建会话数据
        session_data = {
            "agent_id": agent_id,
            "credential_id": credential_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }
        
        # 存储会话
        self._sessions[session_token] = session_data
        self._session_expiry[session_token] = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        # 记录审计日志
        self._log_audit_event("session_created", agent_id, {"session_token": session_token[:8] + "..."})
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """验证会话"""
        # 检查会话是否存在
        session_data = self._sessions.get(session_token)
        if not session_data:
            return None
        
        # 检查会话是否过期
        expiry = self._session_expiry.get(session_token)
        if expiry and datetime.now() > expiry:
            # 删除过期会话
            del self._sessions[session_token]
            del self._session_expiry[session_token]
            return None
        
        # 更新最后活动时间
        session_data["last_activity"] = datetime.now().isoformat()
        
        return session_data
    
    def revoke_session(self, session_token: str) -> bool:
        """撤销会话"""
        if session_token not in self._sessions:
            return False
        
        # 获取Agent ID用于审计日志
        agent_id = self._sessions[session_token].get("agent_id", "unknown")
        
        # 删除会话
        del self._sessions[session_token]
        if session_token in self._session_expiry:
            del self._session_expiry[session_token]
        
        # 记录审计日志
        self._log_audit_event("session_revoked", agent_id, {"session_token": session_token[:8] + "..."})
        
        return True
    
    # ========== 审计日志 ==========
    
    def _log_audit_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> None:
        """记录审计事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
        }
        self._audit_log.append(event)
    
    def get_audit_log(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取审计日志"""
        results = []
        
        for event in reversed(self._audit_log):  # 最新的在前
            # 过滤Agent
            if agent_id and event["agent_id"] != agent_id:
                continue
            
            # 过滤事件类型
            if event_type and event["event_type"] != event_type:
                continue
            
            # 过滤时间范围
            event_time = datetime.fromisoformat(event["timestamp"])
            if start_time and event_time < start_time:
                continue
            if end_time and event_time > end_time:
                continue
            
            results.append(event)
            
            if len(results) >= limit:
                break
        
        return results
    
    # ========== 辅助方法 ==========
    
    def _hash_secret(self, secret: str, salt: str) -> str:
        """哈希密钥"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            secret.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def _generate_token(self) -> str:
        """生成随机令牌"""
        return secrets.token_urlsafe(32)
