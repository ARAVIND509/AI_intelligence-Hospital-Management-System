from pydantic import BaseModel, ConfigDict, EmailStr


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: str | None = None
    password: str


# --------------------------------------------------
# USER LOGIN
# --------------------------------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --------------------------------------------------
# JWT TOKEN
# --------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


# --------------------------------------------------
# TOKEN DATA
# --------------------------------------------------

class TokenData(BaseModel):
    email: str | None = None


# --------------------------------------------------
# USER RESPONSE
# --------------------------------------------------

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# --------------------------------------------------
# CHANGE PASSWORD
# --------------------------------------------------

class ChangePassword(BaseModel):
    current_password: str
    new_password: str