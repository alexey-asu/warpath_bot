from pydantic import BaseModel
from typing import List, Literal

UnitType = Literal[
    "mbt", "medium_tank", "super_heavy",
    "infantry", "howitzer", "rocket_launcher",
    "fighter", "bomber", "heli"
]

class AdditionalSkill(BaseModel):
    code: str
    name: str
    description: str
    best_for: List[UnitType]

class Officer(BaseModel):
    code: str
    name: str
    description: str
    best_for: List[UnitType]
    recommended_skills: List[str]

class SetupRecommendation(BaseModel):
    unit_type: UnitType
    officers: List[str]
    skills: List[str]
    comment: str
