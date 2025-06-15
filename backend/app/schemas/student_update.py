from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.db.models.agenda_item import AgendaItemType


class StudentUpdateBase(BaseModel):
    progress_text: str = Field(..., description="Student's progress since last update")
    challenges_text: str = Field(..., description="Challenges faced by the student")
    next_steps_text: str = Field(..., description="Planned next steps")
    meeting_notes: Optional[str] = Field(None, description="Notes about the meeting")
    will_present: bool = Field(False, description="Whether the student will present at the meeting")


class StudentUpdateCreate(StudentUpdateBase):
    user_id: int = Field(..., description="ID of the student submitting the update")
    meeting_id: Optional[int] = Field(None, description="ID of the meeting this update is for")
    file_ids: Optional[List[int]] = Field(None, description="IDs of files to attach to the update")
    
    def to_agenda_item_create(self):
        """Convert student update to agenda item create format"""
        # Import moved to avoid circular imports
        from app.schemas.agenda_item import AgendaItemCreate
        
        # Build content dict from student update fields
        content = {}
        if self.progress_text:
            content["progress_text"] = self.progress_text
        if self.challenges_text:
            content["challenges_text"] = self.challenges_text
        if self.next_steps_text:
            content["next_steps_text"] = self.next_steps_text
        if self.meeting_notes:
            content["meeting_notes"] = self.meeting_notes
        if self.file_ids:
            content["file_ids"] = self.file_ids
            
        return AgendaItemCreate(
            meeting_id=self.meeting_id,
            user_id=self.user_id,
            item_type=AgendaItemType.STUDENT_UPDATE,
            order_index=0,  # Default order
            title=f"Student Update",
            content=content,
            is_presenting=self.will_present
        )


class StudentUpdateUpdate(BaseModel):
    progress_text: Optional[str] = Field(None, description="Student's progress since last update")
    challenges_text: Optional[str] = Field(None, description="Challenges faced by the student")
    next_steps_text: Optional[str] = Field(None, description="Planned next steps")
    meeting_notes: Optional[str] = Field(None, description="Notes about the meeting")
    will_present: Optional[bool] = Field(None, description="Whether the student will present at the meeting")
    meeting_id: Optional[int] = Field(None, description="ID of the meeting this update is for")
    file_ids: Optional[List[int]] = Field(None, description="IDs of files to attach to the update")


class StudentUpdateInDBBase(StudentUpdateBase):
    id: int
    user_id: int
    meeting_id: Optional[int] = None
    submission_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentUpdate(StudentUpdateInDBBase):
    """Full student update returned from API"""
    pass


class StudentUpdateList(BaseModel):
    """List of student updates returned from API"""
    items: List[StudentUpdate]
    total: int