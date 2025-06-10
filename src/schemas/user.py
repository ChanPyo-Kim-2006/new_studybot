from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match("^[a-zA-Z0-9가-힣_-]+$", v):
            raise ValueError('사용자 이름은 영문자, 숫자, 한글, 밑줄(_), 하이픈(-)만 포함할 수 있습니다.')
        return v

class ChildBase(UserBase):
    region: str = Field(..., min_length=2, max_length=100)
    school_name: str = Field(..., min_length=2, max_length=100)

class ParentBase(UserBase):
    pass

class ChildCreate(ChildBase):
    landmarks: Optional[List[float]] = None

class ParentCreate(ParentBase):
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    child_code: str = Field(..., regex="^STU-[0-9]{4}-[0-9]{4}$")
    
    @validator('password')
    def password_strength(cls, v):
        if not re.match("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", v):
            raise ValueError('비밀번호는 최소 8자 이상이며, 영문자, 숫자, 특수문자를 포함해야 합니다.')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('비밀번호가 일치하지 않습니다.')
        return v

class Child(ChildBase):
    user_id: int
    child_code: str
    created_at: datetime
    is_active: bool = True
    concentration_records: Optional[List[dict]] = []
    
    class Config:
        orm_mode = True

class Parent(ParentBase):
    parent_id: int
    created_at: datetime
    is_active: bool = True
    children: Optional[List[str]] = []  # child_codes
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: Optional[str] = None  # 자녀의 경우 얼굴 인증을 사용하므로 선택적

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: str
    exp: datetime

class ConcentrationRecord(BaseModel):
    user_id: int
    timestamp: datetime
    concentration_score: float = Field(..., ge=0, le=100)
    status: str
    gaze_status: str
    face_detected: bool

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    region: Optional[str] = Field(None, min_length=2, max_length=100)
    school_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None

class ParentUpdate(BaseModel):
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)
    new_password_confirm: Optional[str] = None
    
    @validator('new_password')
    def password_strength(cls, v, values):
        if v is not None:
            if not re.match("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", v):
                raise ValueError('새 비밀번호는 최소 8자 이상이며, 영문자, 숫자, 특수문자를 포함해야 합니다.')
            if 'current_password' not in values or not values['current_password']:
                raise ValueError('현재 비밀번호를 입력해주세요.')
        return v
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        if 'new_password' in values and values['new_password'] is not None:
            if v != values['new_password']:
                raise ValueError('새 비밀번호가 일치하지 않습니다.')
        return v

class UserResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[List[str]] = None

class ChildStatistics(BaseModel):
    user_id: int
    child_code: str
    total_sessions: int
    average_concentration: float
    total_study_time: float  # minutes
    last_session: Optional[datetime]
    concentration_history: List[dict]
    
    class Config:
        orm_mode = True

class ParentDashboard(BaseModel):
    parent_id: int
    children_count: int
    children_stats: List[ChildStatistics]
    
    class Config:
        orm_mode = True

class FaceLandmarks(BaseModel):
    user_id: int
    landmarks: List[float]
    created_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    user_type: str
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime]
    profile_data: dict
    
    class Config:
        orm_mode = True

class UserActivityLog(BaseModel):
    user_id: int
    activity_type: str
    timestamp: datetime
    details: Optional[dict] = None
    
    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None