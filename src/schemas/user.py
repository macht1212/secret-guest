from pydantic import BaseModel, Field, EmailStr


class UserRegisterAdd(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str | None = Field(None)
    last_name: str
    phone: str | None = Field(None)
    city: str | None = Field(None)
    country: str | None = Field(None)
    role: str
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str | None = Field(None)
    last_name: str
    phone: str | None = Field(None)
    city: str | None = Field(None)
    country: str | None = Field(None)
    role: str
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    middle_name: str | None = Field(None)
    last_name: str
    phone: str | None = Field(None)
    city: str | None = Field(None)
    country: str | None = Field(None)
    role: str
    is_verified: bool


class UserWithHashedPassword(User):
    hashed_password: str


class UserRole(BaseModel):
    user_id: int
    role: str


class UserRoleFull(UserRole):
    id: int


class UserIN(BaseModel):
    email: EmailStr
    password: str


class UserPatch(BaseModel):
    email: EmailStr | None = Field(None)
    first_name: str | None = Field(None)
    middle_name: str | None = Field(None)
    last_name: str | None = Field(None)
    phone: str | None = Field(None)
    city: str | None = Field(None)
    country: str | None = Field(None)


class UserPasswordPatch(BaseModel):
    prev_password: str
    new_password: str


class Password(BaseModel):
    hashed_password: str
