"""
Data models for schedule organization
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time

@dataclass
class Class:
    """Represents a single class"""
    id: str
    name: str
    name_en: str
    code: str
    professor: str
    content: str
    content_en: str
    credits: int
    description: str = ""
    description_en: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'code': self.code,
            'professor': self.professor,
            'content': self.content,
            'content_en': self.content_en,
            'credits': self.credits,
            'description': self.description,
            'description_en': self.description_en
        }

@dataclass
class TimeSlot:
    """Represents a time slot for a class"""
    day: str  # Monday, Tuesday, etc.
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    room: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'room': self.room
        }

@dataclass
class Group:
    """Represents a class group/section"""
    id: str
    group_number: str
    class_info: Class
    time_slots: List[TimeSlot] = field(default_factory=list)
    capacity: int = 0
    enrolled: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'group_number': self.group_number,
            'class_info': self.class_info.to_dict(),
            'time_slots': [slot.to_dict() for slot in self.time_slots],
            'capacity': self.capacity,
            'enrolled': self.enrolled,
            'available': self.capacity - self.enrolled
        }

@dataclass
class Schedule:
    """Represents a semester schedule"""
    id: str
    semester: str
    year: int
    period: str  # e.g., "2024-1", "Fall 2024"
    groups: List[Group] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'semester': self.semester,
            'year': self.year,
            'period': self.period,
            'groups': [group.to_dict() for group in self.groups],
            'total_groups': len(self.groups)
        }

@dataclass
class AIAnalysis:
    """Represents AI analysis of class content"""
    class_id: str
    summary: str
    summary_en: str
    key_topics: List[str]
    key_topics_en: List[str]
    difficulty_level: str
    prerequisites: List[str] = field(default_factory=list)
    recommendations: str = ""
    recommendations_en: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'class_id': self.class_id,
            'summary': self.summary,
            'summary_en': self.summary_en,
            'key_topics': self.key_topics,
            'key_topics_en': self.key_topics_en,
            'difficulty_level': self.difficulty_level,
            'prerequisites': self.prerequisites,
            'recommendations': self.recommendations,
            'recommendations_en': self.recommendations_en
        }
