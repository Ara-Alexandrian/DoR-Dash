from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator

from app.db.models.agenda_item import AgendaItemType


# Base schemas
class AgendaItemBase(BaseModel):
    meeting_id: int
    user_id: int
    item_type: AgendaItemType
    order_index: int = 0
    title: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    is_presenting: bool = False


class AgendaItemCreate(AgendaItemBase):
    pass


class AgendaItemUpdate(BaseModel):
    meeting_id: Optional[int] = None
    order_index: Optional[int] = None
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    is_presenting: Optional[bool] = None


# File schema for agenda items
class AgendaItemFile(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    upload_date: datetime


# Full agenda item response
class AgendaItem(AgendaItemBase):
    id: int
    user_name: str
    files: List[AgendaItemFile] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Specialized schemas for different content types
class StudentUpdateCreate(BaseModel):
    meeting_id: int
    user_id: int
    progress_text: str
    challenges_text: str = ""
    next_steps_text: str = ""
    meeting_notes: str = ""
    will_present: bool = False
    order_index: int = 0

    def to_agenda_item_create(self) -> AgendaItemCreate:
        """Convert to unified agenda item create schema"""
        return AgendaItemCreate(
            meeting_id=self.meeting_id,
            user_id=self.user_id,
            item_type=AgendaItemType.STUDENT_UPDATE,
            order_index=self.order_index,
            title=f"Student Update",  # Will be auto-generated with user name
            content={
                "progress_text": self.progress_text,
                "challenges_text": self.challenges_text,
                "next_steps_text": self.next_steps_text,
                "meeting_notes": self.meeting_notes
            },
            is_presenting=self.will_present
        )


class StudentUpdateUpdate(BaseModel):
    progress_text: Optional[str] = None
    challenges_text: Optional[str] = None
    next_steps_text: Optional[str] = None
    meeting_notes: Optional[str] = None
    will_present: Optional[bool] = None
    meeting_id: Optional[int] = None

    def to_agenda_item_update(self) -> AgendaItemUpdate:
        """Convert to unified agenda item update schema"""
        content_updates = {}
        if self.progress_text is not None:
            content_updates["progress_text"] = self.progress_text
        if self.challenges_text is not None:
            content_updates["challenges_text"] = self.challenges_text
        if self.next_steps_text is not None:
            content_updates["next_steps_text"] = self.next_steps_text
        if self.meeting_notes is not None:
            content_updates["meeting_notes"] = self.meeting_notes

        return AgendaItemUpdate(
            meeting_id=self.meeting_id,
            content=content_updates if content_updates else None,
            is_presenting=self.will_present
        )


class FacultyUpdateCreate(BaseModel):
    meeting_id: int
    user_id: int
    announcements_text: str = ""
    announcement_type: str = "general"
    projects_text: str = ""
    project_status_text: str = ""
    faculty_questions: str = ""
    is_presenting: bool = False
    order_index: int = 0

    @validator('announcement_type')
    def validate_announcement_type(cls, v):
        valid_types = ['general', 'urgent', 'deadline']
        if v not in valid_types:
            raise ValueError(f'announcement_type must be one of {valid_types}')
        return v

    def to_agenda_item_create(self) -> AgendaItemCreate:
        """Convert to unified agenda item create schema"""
        return AgendaItemCreate(
            meeting_id=self.meeting_id,
            user_id=self.user_id,
            item_type=AgendaItemType.FACULTY_UPDATE,
            order_index=self.order_index,
            title=f"Faculty Update",  # Will be auto-generated with user name
            content={
                "announcements_text": self.announcements_text,
                "announcement_type": self.announcement_type,
                "projects_text": self.projects_text,
                "project_status_text": self.project_status_text,
                "faculty_questions": self.faculty_questions
            },
            is_presenting=self.is_presenting
        )


class FacultyUpdateUpdate(BaseModel):
    announcements_text: Optional[str] = None
    announcement_type: Optional[str] = None
    projects_text: Optional[str] = None
    project_status_text: Optional[str] = None
    faculty_questions: Optional[str] = None
    is_presenting: Optional[bool] = None
    meeting_id: Optional[int] = None

    @validator('announcement_type')
    def validate_announcement_type(cls, v):
        if v is not None:
            valid_types = ['general', 'urgent', 'deadline']
            if v not in valid_types:
                raise ValueError(f'announcement_type must be one of {valid_types}')
        return v

    def to_agenda_item_update(self) -> AgendaItemUpdate:
        """Convert to unified agenda item update schema"""
        content_updates = {}
        if self.announcements_text is not None:
            content_updates["announcements_text"] = self.announcements_text
        if self.announcement_type is not None:
            content_updates["announcement_type"] = self.announcement_type
        if self.projects_text is not None:
            content_updates["projects_text"] = self.projects_text
        if self.project_status_text is not None:
            content_updates["project_status_text"] = self.project_status_text
        if self.faculty_questions is not None:
            content_updates["faculty_questions"] = self.faculty_questions

        return AgendaItemUpdate(
            meeting_id=self.meeting_id,
            content=content_updates if content_updates else None,
            is_presenting=self.is_presenting
        )


# Legacy compatibility schemas (for backward compatibility during transition)
class StudentUpdate(BaseModel):
    """Legacy student update schema for backward compatibility"""
    id: int
    user_id: int
    user_name: str
    progress_text: str
    challenges_text: str
    next_steps_text: str
    meeting_notes: str
    will_present: bool
    meeting_id: Optional[int]
    files: List[AgendaItemFile] = []
    submission_date: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_agenda_item(cls, agenda_item: AgendaItem) -> "StudentUpdate":
        """Convert from unified agenda item to legacy format"""
        if agenda_item.item_type != AgendaItemType.STUDENT_UPDATE:
            raise ValueError("Can only convert student update agenda items")
        
        content = agenda_item.content
        return cls(
            id=agenda_item.id,
            user_id=agenda_item.user_id,
            user_name=agenda_item.user_name,
            progress_text=content.get("progress_text", ""),
            challenges_text=content.get("challenges_text", ""),
            next_steps_text=content.get("next_steps_text", ""),
            meeting_notes=content.get("meeting_notes", ""),
            will_present=agenda_item.is_presenting,
            meeting_id=agenda_item.meeting_id,
            files=agenda_item.files,
            submission_date=agenda_item.created_at,
            created_at=agenda_item.created_at,
            updated_at=agenda_item.updated_at
        )


class FacultyUpdate(BaseModel):
    """Legacy faculty update schema for backward compatibility"""
    id: int
    user_id: int
    user_name: str
    meeting_id: Optional[int]
    announcements_text: str
    announcement_type: str
    projects_text: str
    project_status_text: str
    faculty_questions: str
    is_presenting: bool
    files: List[AgendaItemFile] = []
    submission_date: datetime
    submitted_at: datetime  # For frontend compatibility
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_agenda_item(cls, agenda_item: AgendaItem) -> "FacultyUpdate":
        """Convert from unified agenda item to legacy format"""
        if agenda_item.item_type != AgendaItemType.FACULTY_UPDATE:
            raise ValueError("Can only convert faculty update agenda items")
        
        content = agenda_item.content
        return cls(
            id=agenda_item.id,
            user_id=agenda_item.user_id,
            user_name=agenda_item.user_name,
            meeting_id=agenda_item.meeting_id,
            announcements_text=content.get("announcements_text", ""),
            announcement_type=content.get("announcement_type", "general"),
            projects_text=content.get("projects_text", ""),
            project_status_text=content.get("project_status_text", ""),
            faculty_questions=content.get("faculty_questions", ""),
            is_presenting=agenda_item.is_presenting,
            files=agenda_item.files,
            submission_date=agenda_item.created_at,
            submitted_at=agenda_item.created_at,  # For frontend compatibility
            created_at=agenda_item.created_at,
            updated_at=agenda_item.updated_at
        )


# List schemas
class AgendaItemList(BaseModel):
    items: List[AgendaItem]
    total: int


class StudentUpdateList(BaseModel):
    items: List[StudentUpdate]
    total: int


class FacultyUpdateList(BaseModel):
    items: List[FacultyUpdate]
    total: int