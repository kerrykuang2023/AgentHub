"""
技能模块

定义 Skill 的创建、管理、验证和执行。
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


@dataclass
class SkillParameter:
    """技能参数定义"""
    name: str
    type: str  # string, integer, float, boolean, array, object
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None  # 可选值列表


@dataclass
class SkillOutput:
    """技能输出定义"""
    type: str
    description: str
    schema: Optional[Dict[str, Any]] = None


@dataclass
class SkillMetadata:
    """技能元数据"""
    skill_id: str
    name: str
    version: str
    description: str
    author: str
    category: str  # 分类：数据分析、自动化、通信等
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    
    # 依赖
    prerequisites: List[str] = field(default_factory=list)  # 前置技能
    dependencies: List[str] = field(default_factory=list)  # 依赖包
    
    # 许可和文档
    license: str = "MIT"
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None


class Skill:
    """
    技能类
    
    表示一个可学习、可执行的技能。
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        author: str,
        category: str,
        version: str = "1.0.0",
        skill_id: Optional[str] = None,
    ):
        self.metadata = SkillMetadata(
            skill_id=skill_id or str(uuid.uuid4()),
            name=name,
            version=version,
            description=description,
            author=author,
            category=category,
        )
        
        # 参数和输出定义
        self.parameters: Dict[str, SkillParameter] = {}
        self.outputs: Dict[str, SkillOutput] = {}
        
        # 执行逻辑
        self._implementation: Optional[Callable] = None
        self._code: Optional[str] = None
        
        # 测试用例
        self.test_cases: List[Dict[str, Any]] = []
        
        # 学习资源
        self.learning_resources: Dict[str, Any] = {
            "documentation": None,
            "video_tutorials": [],
            "example_projects": [],
            "practice_exercises": [],
        }
        
    def add_parameter(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = True,
        default: Optional[Any] = None,
        enum: Optional[List[Any]] = None,
    ) -> "Skill":
        """添加参数"""
        self.parameters[name] = SkillParameter(
            name=name,
            type=type,
            description=description,
            required=required,
            default=default,
            enum=enum,
        )
        return self
    
    def add_output(
        self,
        name: str,
        type: str,
        description: str,
        schema: Optional[Dict[str, Any]] = None,
    ) -> "Skill":
        """添加输出"""
        self.outputs[name] = SkillOutput(
            type=type,
            description=description,
            schema=schema,
        )
        return self
    
    def set_implementation(self, func: Callable) -> "Skill":
        """设置实现函数"""
        self._implementation = func
        return self
    
    def set_code(self, code: str) -> "Skill":
        """设置代码字符串"""
        self._code = code
        return self
    
    def add_test_case(self, inputs: Dict[str, Any], expected_output: Any) -> "Skill":
        """添加测试用例"""
        self.test_cases.append({
            "inputs": inputs,
            "expected_output": expected_output,
        })
        return self
    
    def validate(self) -> List[str]:
        """验证技能定义是否完整"""
        errors = []
        
        if not self.metadata.name:
            errors.append("Skill name is required")
        
        if not self.metadata.description:
            errors.append("Skill description is required")
            
        if not self._implementation and not self._code:
            errors.append("Skill must have either implementation or code")
        
        # 验证参数类型
        valid_types = ["string", "integer", "float", "boolean", "array", "object"]
        for param in self.parameters.values():
            if param.type not in valid_types:
                errors.append(f"Invalid parameter type: {param.type}")
        
        return errors
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        if not self._implementation:
            raise ValueError("Skill has no implementation")
        
        # 验证必需参数
        for param_name, param in self.parameters.items():
            if param.required and param_name not in kwargs and param.default is None:
                raise ValueError(f"Missing required parameter: {param_name}")
        
        # 填充默认值
        for param_name, param in self.parameters.items():
            if param_name not in kwargs and param.default is not None:
                kwargs[param_name] = param.default
        
        # 执行
        result = self._implementation(**kwargs)
        
        # 更新使用统计
        self.metadata.downloads += 1
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metadata": {
                "skill_id": self.metadata.skill_id,
                "name": self.metadata.name,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "category": self.metadata.category,
                "tags": self.metadata.tags,
                "created_at": self.metadata.created_at.isoformat(),
                "updated_at": self.metadata.updated_at.isoformat(),
                "downloads": self.metadata.downloads,
                "rating": self.metadata.rating,
                "rating_count": self.metadata.rating_count,
                "prerequisites": self.metadata.prerequisites,
                "dependencies": self.metadata.dependencies,
                "license": self.metadata.license,
                "documentation_url": self.metadata.documentation_url,
                "repository_url": self.metadata.repository_url,
            },
            "parameters": {
                name: {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default,
                    "enum": param.enum,
                }
                for name, param in self.parameters.items()
            },
            "outputs": {
                name: {
                    "type": output.type,
                    "description": output.description,
                    "schema": output.schema,
                }
                for name, output in self.outputs.items()
            },
            "test_cases": self.test_cases,
            "learning_resources": self.learning_resources,
            "has_implementation": self._implementation is not None,
            "has_code": self._code is not None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """从字典创建"""
        meta = data["metadata"]
        skill = cls(
            name=meta["name"],
            description=meta["description"],
            author=meta["author"],
            category=meta["category"],
            version=meta["version"],
            skill_id=meta["skill_id"],
        )
        
        # 恢复其他元数据
        skill.metadata.tags = meta.get("tags", [])
        skill.metadata.downloads = meta.get("downloads", 0)
        skill.metadata.rating = meta.get("rating", 0.0)
        skill.metadata.rating_count = meta.get("rating_count", 0)
        skill.metadata.prerequisites = meta.get("prerequisites", [])
        skill.metadata.dependencies = meta.get("dependencies", [])
        skill.metadata.license = meta.get("license", "MIT")
        skill.metadata.documentation_url = meta.get("documentation_url")
        skill.metadata.repository_url = meta.get("repository_url")
        
        # 恢复参数
        for name, param_data in data.get("parameters", {}).items():
            skill.add_parameter(
                name=name,
                type=param_data["type"],
                description=param_data["description"],
                required=param_data.get("required", True),
                default=param_data.get("default"),
                enum=param_data.get("enum"),
            )
        
        # 恢复输出
        for name, output_data in data.get("outputs", {}).items():
            skill.add_output(
                name=name,
                type=output_data["type"],
                description=output_data["description"],
                schema=output_data.get("schema"),
            )
        
        # 恢复测试用例
        skill.test_cases = data.get("test_cases", [])
        
        # 恢复学习资源
        skill.learning_resources = data.get("learning_resources", {
            "documentation": None,
            "video_tutorials": [],
            "example_projects": [],
            "practice_exercises": [],
        })
        
        return skill


class SkillRegistry:
    """
    技能注册表
    
    管理所有可用的技能，提供技能的注册、发现、加载和执行。
    """
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._categories: Dict[str, List[str]] = {}
        self._author_index: Dict[str, List[str]] = {}
        
    def register(self, skill: Skill) -> None:
        """注册技能"""
        skill_id = skill.metadata.skill_id
        
        # 检查是否已存在
        if skill_id in self._skills:
            raise ValueError(f"Skill {skill_id} already registered")
        
        # 添加到技能字典
        self._skills[skill_id] = skill
        
        # 添加到分类索引
        category = skill.metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(skill_id)
        
        # 添加到作者索引
        author = skill.metadata.author
        if author not in self._author_index:
            self._author_index[author] = []
        self._author_index[author].append(skill_id)
        
    def unregister(self, skill_id: str) -> None:
        """注销技能"""
        if skill_id not in self._skills:
            raise ValueError(f"Skill {skill_id} not found")
        
        skill = self._skills[skill_id]
        
        # 从分类索引中移除
        category = skill.metadata.category
        if category in self._categories:
            self._categories[category].remove(skill_id)
        
        # 从作者索引中移除
        author = skill.metadata.author
        if author in self._author_index:
            self._author_index[author].remove(skill_id)
        
        # 从技能字典中移除
        del self._skills[skill_id]
        
    def get(self, skill_id: str) -> Skill:
        """获取技能"""
        if skill_id not in self._skills:
            raise ValueError(f"Skill {skill_id} not found")
        return self._skills[skill_id]
        
    def list_all(self) -> List[Skill]:
        """列出所有技能"""
        return list(self._skills.values())
        
    def list_by_category(self, category: str) -> List[Skill]:
        """按分类列出技能"""
        if category not in self._categories:
            return []
        return [self._skills[skill_id] for skill_id in self._categories[category]]
        
    def list_by_author(self, author: str) -> List[Skill]:
        """按作者列出技能"""
        if author not in self._author_index:
            return []
        return [self._skills[skill_id] for skill_id in self._author_index[author]]
        
    def search(self, query: str) -> List[Skill]:
        """搜索技能"""
        results = []
        query = query.lower()
        
        for skill in self._skills.values():
            # 搜索名称
            if query in skill.metadata.name.lower():
                results.append(skill)
                continue
            
            # 搜索描述
            if query in skill.metadata.description.lower():
                results.append(skill)
                continue
            
            # 搜索标签
            for tag in skill.metadata.tags:
                if query in tag.lower():
                    results.append(skill)
                    break
        
        return results
        
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self._categories.keys())
        
    def get_popular(self, limit: int = 10) -> List[Skill]:
        """获取热门技能"""
        sorted_skills = sorted(
            self._skills.values(),
            key=lambda s: s.metadata.downloads,
            reverse=True
        )
        return sorted_skills[:limit]
        
    def get_top_rated(self, limit: int = 10) -> List[Skill]:
        """获取评分最高技能"""
        sorted_skills = sorted(
            self._skills.values(),
            key=lambda s: s.metadata.rating,
            reverse=True
        )
        return sorted_skills[:limit]
