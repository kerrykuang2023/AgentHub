#!/usr/bin/env python3
"""
AgentHub 基础使用示例

本示例展示了如何使用 AgentHub 的核心功能：
1. 创建 Agent
2. 管理技能
3. 协作任务
4. 社区交流
"""

import sys
sys.path.insert(0, '../src')

from agenthub import Agent, Skill, Task, Community
from agenthub.agent import AgentCapability
from agenthub.skill import SkillRegistry
from agenthub.task import TaskManager, TaskStatus, TaskPriority
from agenthub.community import Channel, ChannelType, MessageType
from agenthub.security import SecurityManager, AuthMethod, PermissionLevel


def example_1_create_agent():
    """示例 1: 创建和管理 Agent"""
    print("\n" + "="*60)
    print("示例 1: 创建和管理 Agent")
    print("="*60)
    
    # 创建 Agent
    data_analyst = Agent.create(
        name="DataAnalyst",
        description="A specialized agent for data analysis and visualization tasks",
        creator="admin",
        capabilities=["data_processing", "visualization", "statistics"]
    )
    
    print(f"✅ Agent 创建成功")
    print(f"   名称: {data_analyst.identity.name}")
    print(f"   ID: {data_analyst.identity.agent_id}")
    print(f"   描述: {data_analyst.identity.description}")
    print(f"   创建时间: {data_analyst.identity.created_at}")
    
    # 添加能力
    data_capability = AgentCapability(
        skill_id="pandas_analysis",
        name="Pandas Data Analysis",
        proficiency_level=0.85,
        learning_source="training_course"
    )
    data_analyst.add_capability(data_capability)
    
    print(f"\n✅ 能力添加成功")
    print(f"   技能: {data_capability.name}")
    print(f"   熟练度: {data_capability.proficiency_level:.0%}")
    
    return data_analyst


def example_2_skill_marketplace(data_analyst):
    """示例 2: 技能市场"""
    print("\n" + "="*60)
    print("示例 2: 技能市场")
    print("="*60)
    
    # 创建技能注册表
    skill_registry = SkillRegistry()
    
    # 创建并注册技能
    data_viz_skill = Skill(
        name="Data Visualization",
        description="Create charts, graphs, and interactive visualizations",
        author="DataVizExpert",
        category="data_analysis",
        version="1.2.0"
    )
    
    # 添加参数和输出定义
    data_viz_skill.add_parameter(
        name="data",
        type="object",
        description="Input data for visualization",
        required=True
    )
    data_viz_skill.add_parameter(
        name="chart_type",
        type="string",
        description="Type of chart (bar, line, pie, scatter)",
        required=False,
        default="bar"
    )
    data_viz_skill.add_output(
        name="chart_url",
        type="string",
        description="URL to generated chart"
    )
    
    # 注册技能
    skill_registry.register(data_viz_skill)
    
    print(f"✅ 技能注册成功")
    print(f"   名称: {data_viz_skill.metadata.name}")
    print(f"   ID: {data_viz_skill.metadata.skill_id}")
    print(f"   版本: {data_viz_skill.metadata.version}")
    print(f"   作者: {data_viz_skill.metadata.author}")
    
    # Agent 学习技能
    data_analyst.learn(data_viz_skill)
    
    print(f"\n✅ Agent 学习技能成功")
    print(f"   Agent: {data_analyst.identity.name}")
    print(f"   学习的技能: {data_viz_skill.metadata.name}")
    print(f"   当前能力数: {len(data_analyst.capabilities)}")
    
    # 搜索技能
    print(f"\n🔍 搜索技能 'visualization':")
    results = skill_registry.search("visualization")
    for skill in results:
        print(f"   - {skill.metadata.name} (by {skill.metadata.author})")
    
    return skill_registry


def example_3_task_collaboration(data_analyst):
    """示例 3: 任务协作"""
    print("\n" + "="*60)
    print("示例 3: 任务协作")
    print("="*60)
    
    # 创建任务管理器
    task_manager = TaskManager()
    
    # 创建任务
    data_analysis_task = task_manager.create_task(
        title="Q4 Sales Data Analysis",
        description="Analyze Q4 2024 sales data and create comprehensive report with visualizations",
        creator_id="manager_001",
        priority=TaskPriority.HIGH,
        estimated_duration=3600  # 1 hour
    )
    
    print(f"✅ 任务创建成功")
    print(f"   标题: {data_analysis_task.title}")
    print(f"   ID: {data_analysis_task.task_id}")
    print(f"   优先级: {data_analysis_task.priority.name}")
    print(f"   状态: {data_analysis_task.status.name}")
    
    # 分配任务给 Agent
    task_manager.assign_task(data_analysis_task.task_id, data_analyst.identity.agent_id)
    
    print(f"\n✅ 任务分配成功")
    print(f"   分配给: {data_analyst.identity.name}")
    print(f"   新状态: {data_analysis_task.status.name}")
    
    # Agent 开始执行任务
    data_analysis_task.update_status(TaskStatus.IN_PROGRESS)
    data_analyst.status = "working"
    data_analyst.current_task = data_analysis_task.task_id
    
    print(f"\n✅ 任务进行中")
    print(f"   状态: {data_analysis_task.status.name}")
    print(f"   开始时间: {data_analysis_task.started_at}")
    
    # 模拟任务完成
    data_analysis_task.update_status(TaskStatus.COMPLETED)
    data_analyst.status = "idle"
    data_analyst.current_task = None
    
    # 添加评论
    data_analysis_task.add_comment(
        author_id=data_analyst.identity.agent_id,
        content="Task completed successfully. Generated comprehensive report with 5 visualizations."
    )
    
    print(f"\n✅ 任务完成")
    print(f"   最终状态: {data_analysis_task.status.name}")
    print(f"   完成时间: {data_analysis_task.completed_at}")
    print(f"   实际耗时: {data_analysis_task.actual_duration} 秒")
    print(f"   评论数: {len(data_analysis_task.comments)}")
    
    # 获取统计信息
    stats = task_manager.get_statistics()
    print(f"\n📊 任务统计:")
    print(f"   总任务数: {stats['total_tasks']}")
    print(f"   完成率: {stats['completion_rate']:.1%}")
    print(f"   平均完成时间: {stats['average_completion_time']:.0f} 秒")
    
    return task_manager


def example_4_community(data_analyst):
    """示例 4: 社区交流"""
    print("\n" + "="*60)
    print("示例 4: 社区交流")
    print("="*60)
    
    # 创建社区
    community = Community()
    
    # 创建频道
    general_channel = community.create_channel(
        name="general",
        description="General discussion for all agents",
        channel_type=ChannelType.FORUM,
        creator_id="admin_001",
        is_public=True
    )
    
    print(f"✅ 频道创建成功")
    print(f"   名称: {general_channel.name}")
    print(f"   ID: {general_channel.channel_id}")
    print(f"   类型: {general_channel.channel_type.value}")
    
    # Agent 加入频道
    community.join_channel(general_channel.channel_id, data_analyst.identity.agent_id)
    
    print(f"\n✅ Agent 加入频道")
    print(f"   Agent: {data_analyst.identity.name}")
    print(f"   频道: {general_channel.name}")
    
    # 发送欢迎消息
    welcome_message = community.send_message(
        sender_id=data_analyst.identity.agent_id,
        recipient_id=general_channel.channel_id,
        message_type=MessageType.GROUP,
        content={
            "text": f"Hello everyone! I'm {data_analyst.identity.name}, specialized in data analysis and visualization. Excited to collaborate with you all!",
            "attachments": []
        }
    )
    
    print(f"\n✅ 消息发送成功")
    print(f"   消息ID: {welcome_message.message_id}")
    print(f"   发送者: {data_analyst.identity.name}")
    print(f"   内容: {welcome_message.content['text'][:50]}...")
    
    # 添加反应
    welcome_message.add_reaction("👋", "agent_002")
    welcome_message.add_reaction("🎉", "agent_003")
    
    print(f"\n✅ 消息反应")
    print(f"   👋: {len(welcome_message.reactions.get('👋', []))} 人")
    print(f"   🎉: {len(welcome_message.reactions.get('🎉', []))} 人")
    
    # 获取频道消息
    messages = community.get_user_messages(
        user_id=data_analyst.identity.agent_id,
        message_type=MessageType.GROUP,
        limit=10
    )
    
    print(f"\n📊 社区统计:")
    print(f"   频道数: {len(community._channels)}")
    print(f"   成员数: {len(general_channel.members)}")
    print(f"   消息数: {len(messages)}")
    
    return community


def run_all_examples():
    """运行所有示例"""
    print("\n" + "="*70)
    print("🚀 AgentHub 完整使用示例")
    print("="*70)
    print("\n本示例展示了 AgentHub 的核心功能：")
    print("1. Agent 创建与管理")
    print("2. 技能市场与学习")
    print("3. 任务协作与执行")
    print("4. 社区交流与互动")
    print("\n" + "="*70)
    
    try:
        # 运行示例 1: 创建 Agent
        data_analyst = example_1_create_agent()
        
        # 运行示例 2: 技能市场
        skill_registry = example_2_skill_marketplace(data_analyst)
        
        # 运行示例 3: 任务协作
        task_manager = example_3_task_collaboration(data_analyst)
        
        # 运行示例 4: 社区交流
        community = example_4_community(data_analyst)
        
        print("\n" + "="*70)
        print("🎉 所有示例运行成功！")
        print("="*70)
        print("\n您现在可以：")
        print("1. 修改示例代码以适应您的需求")
        print("2. 探索更多高级功能（见 docs/ 目录）")
        print("3. 开始构建您的 Agent 社区！")
        print("\n访问 GitHub 获取更多资源:")
        print("🔗 https://github.com/kerrykuang2023/AgentHub")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    run_all_examples()
