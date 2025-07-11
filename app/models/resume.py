from dataclasses import dataclass
from datetime import datetime


@dataclass
class Resume:
    id: str
    user_id: str
    content: str
    filename: str
    created_at: datetime
    updated_at: datetime
