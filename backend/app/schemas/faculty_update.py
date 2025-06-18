from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from app.db.models.agenda_item import AgendaItemType


class AnnouncementType(str, Enum):
    GENERAL = "general"
    URGENT = "urgent"
    DEADLINE = "deadline"
    FUNDING = "funding"


class FacultyUpdateBase(BaseModel):
    announcements_text: Optional[str] = Field(None, description="Faculty announcements for students")
    announcement_type: AnnouncementType = Field(AnnouncementType.GENERAL, description="Type of announcement")
    projects_text: Optional[str] = Field(None, description="Current project updates")
    project_status_text: Optional[str] = Field(None, description="Status of ongoing projects")
    faculty_questions: Optional[str] = Field(None, description="Questions for students")
    is_presenting: bool = Field(False, description="Whether faculty will be presenting")


class FacultyUpdateCreate(FacultyUpdateBase):
    user_id: int = Field(..., description="ID of the faculty member submitting the update")
    meeting_id: Optional[int] = Field(None, description="ID of the meeting this update is for")
    
    def to_agenda_item_create(self):
        """Convert faculty update to agenda item create format"""
        # Import moved to avoid circular imports
        from app.schemas.agenda_item import AgendaItemCreate
        
        # Build content dict from faculty update fields
        content = {}
        if self.announcements_text:
            content["announcements_text"] = self.announcements_text
        if self.announcement_type:
            content["announcement_type"] = self.announcement_type.value
        if self.projects_text:
            content["projects_text"] = self.projects_text
        if self.project_status_text:
            content["project_status_text"] = self.project_status_text
        if self.faculty_questions:
            content["faculty_questions"] = self.faculty_questions
            
        return AgendaItemCreate(
            meeting_id=self.meeting_id,
            user_id=self.user_id,
            item_type=AgendaItemType.FACULTY_UPDATE,
            order_index=0,  # Default order
            title=f"Faculty Update - {self.announcement_type.value.title()}",
            content=content,
            is_presenting=self.is_presenting
        )


class FacultyUpdateUpdate(BaseModel):
    announcements_text: Optional[str] = Field(None, description="Faculty announcements for students")
    announcement_type: Optional[AnnouncementType] = Field(None, description="Type of announcement")
    projects_text: Optional[str] = Field(None, description="Current project updates")
    project_status_text: Optional[str] = Field(None, description="Status of ongoing projects")
    faculty_questions: Optional[str] = Field(None, description="Questions for students")
    is_presenting: Optional[bool] = Field(None, description="Whether faculty will be presenting")
    meeting_id: Optional[int] = Field(None, description="ID of the meeting this update is for")


class FacultyUpdateInDBBase(FacultyUpdateBase):
    id: int
    user_id: int
    meeting_id: Optional[int] = None
    submission_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacultyUpdate(FacultyUpdateInDBBase):
    """Full faculty update returned from API"""
    pass


class FacultyUpdateList(BaseModel):
    """List of faculty updates returned from API"""
    items: List[FacultyUpdate]
    total: int