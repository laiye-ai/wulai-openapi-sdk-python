"""
配置类
1. 更新机器人回复配置
"""
from wulaisdk.response import BaseModel


class QABotConfig(BaseModel):
    """
    问答对话配置
    """
    similar_response_enabled: bool
    auto_response_threshold: int

    def __init__(self, similar_response_enabled: bool, auto_response_threshold: int) -> None:
        self.similar_response_enabled = similar_response_enabled
        self.auto_response_threshold = auto_response_threshold


class TaskBotConfig(BaseModel):
    """
    任务对话配置
    """
    auto_response_threshold: int

    def __init__(self, auto_response_threshold: int) -> None:
        self.auto_response_threshold = auto_response_threshold


class BotConfig(BaseModel):
    """
    对话配置
    """
    qa_bot_config: QABotConfig
    task_bot_config: TaskBotConfig

    def __init__(self, qa_bot_config: QABotConfig, task_bot_config: TaskBotConfig) -> None:
        self.qa_bot_config = QABotConfig.from_dict(qa_bot_config)
        self.task_bot_config = TaskBotConfig.from_dict(task_bot_config)


class EConfig(BaseModel):
    """
    兜底回复/转人工配置
    """
    enabled: bool

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled


class AppConfig(BaseModel):
    """
    机器人配置
    """
    bot_config: BotConfig
    default_response_config: EConfig
    customer_service_config: EConfig

    def __init__(self, bot_config: BotConfig, default_response_config: EConfig, customer_service_config: EConfig) -> None:
        self.bot_config = BotConfig.from_dict(bot_config)
        self.default_response_config = EConfig.from_dict(default_response_config)
        self.customer_service_config = EConfig.from_dict(customer_service_config)


class UpdateConfig(BaseModel):
    """
    更新机器人配置
    """
    app_config: AppConfig

    def __init__(self, app_config: AppConfig) -> None:
        self.app_config = AppConfig.from_dict(app_config)
