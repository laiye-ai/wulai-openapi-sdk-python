"""
统计类
1. 添加用户满意度评价
2. 查询问答满意度评价统计列表（知识点粒度，日报）
3. 查询问答召回数统计列表（日报）
4. 查询问答召回数统计列表（知识点粒度，日报）
"""

from typing import List
from wulaisdk.response import BaseModel


class SatisfactionStats(BaseModel):
    """
    满意度
    """
    thumb_up_count: int
    wrong_answer_count: int
    bad_answer_count: int

    def __init__(self, thumb_up_count: int, wrong_answer_count: int, bad_answer_count: int) -> None:
        self.thumb_up_count = thumb_up_count
        self.wrong_answer_count = wrong_answer_count
        self.bad_answer_count = bad_answer_count


class QASatisfactionKnowledgeStat(BaseModel):
    """
    知识点粒度的问答满意度列表
    """
    knowledge_id: int
    satisfaction_stats: SatisfactionStats
    standard_question: str

    def __init__(self, knowledge_id: int, satisfaction_stats: SatisfactionStats, standard_question: str) -> None:
        self.knowledge_id = knowledge_id
        self.satisfaction_stats = SatisfactionStats.from_dict(satisfaction_stats)
        self.standard_question = standard_question


class StatsQASatisfactionKnowledgeDaily(BaseModel):
    """
    查询问答满意度评价统计列表（知识点粒度，日报）
    """
    page_count: int
    qa_satisfaction_knowledge_stats: List[QASatisfactionKnowledgeStat]

    def __init__(self, page_count: int, qa_satisfaction_knowledge_stats: List[QASatisfactionKnowledgeStat]) -> None:
        self.page_count = page_count
        self.qa_satisfaction_knowledge_stats = [
            QASatisfactionKnowledgeStat.from_dict(qsks) for qsks in qa_satisfaction_knowledge_stats
        ]


class MessageStats(BaseModel):
    """
    消息统计
    """
    receive_count: int

    def __init__(self, receive_count: int) -> None:
        self.receive_count = receive_count


class QARecallStats(BaseModel):
    """
    问答召回数
    """
    recall_count: int

    def __init__(self, recall_count: int) -> None:
        self.recall_count = recall_count


class QARecallDailyStat(BaseModel):
    """
    (天粒度的的问答召回数列表)
    """
    date: str
    message_stats: MessageStats
    qa_recall_stats: QARecallStats

    def __init__(self, date: str, message_stats: MessageStats, qa_recall_stats: QARecallStats) -> None:
        self.date = date
        self.message_stats = MessageStats.from_dict(message_stats)
        self.qa_recall_stats = QARecallStats.from_dict(qa_recall_stats)


class StatsQARecallDaily(BaseModel):
    """
    查询问答召回数统计列表（日报）
    """
    qa_recall_daily_stats: List[QARecallDailyStat]

    def __init__(self, qa_recall_daily_stats: List[QARecallDailyStat]) -> None:
        self.qa_recall_daily_stats = [QARecallDailyStat.from_dict(qrds) for qrds in qa_recall_daily_stats]


class QARecallKnowledgeStat(BaseModel):
    """
    知识点粒度的问答满意度列表
    """
    knowledge_id: int
    standard_question: str
    qa_recall_stats: QARecallStats

    def __init__(self, knowledge_id: int, standard_question: str, qa_recall_stats: QARecallStats) -> None:
        self.knowledge_id = knowledge_id
        self.standard_question = standard_question
        self.qa_recall_stats = QARecallStats.from_dict(qa_recall_stats)


class StatasQARecallDailyKnowledges(BaseModel):
    """
    查询问答召回数统计列表（知识点粒度，日报）
    """
    qa_recall_knowledge_stats: List[QARecallKnowledgeStat]
    page_count: int

    def __init__(self, qa_recall_knowledge_stats: List[QARecallKnowledgeStat], page_count: int) -> None:
        self.qa_recall_knowledge_stats = [QARecallKnowledgeStat.from_dict(qcks) for qcks in qa_recall_knowledge_stats]
        self.page_count = page_count
