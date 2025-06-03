from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AnnouncementType(str, Enum):
    GENERAL = "general"
    URGENT = "urgent"
    DEADLINE = "deadline"


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