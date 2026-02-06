import aiosqlite
import asyncio
from typing import List, Dict
from models import Officer, AdditionalSkill, SetupRecommendation, UnitType

DB_PATH = "warpath_knowledge.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS officers (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                best_for TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                best_for TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS setups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_type TEXT NOT NULL,
                officers TEXT NOT NULL,
                skills TEXT NOT NULL,
                comment TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_officers() -> Dict[str, Officer]:
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await db.execute("SELECT * FROM officers")
        data = await rows.fetchall()
        return {
            row[0]: Officer(
                code=row[0], name=row[1], description=row[2],
                best_for=eval(row[3]), recommended_skills=[]
            ) for row in data
        }

async def get_skills() -> Dict[str, AdditionalSkill]:
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await db.execute("SELECT * FROM skills")
        data = await rows.fetchall()
        return {
            row[0]: AdditionalSkill(
                code=row[0], name=row[1], description=row[2],
                best_for=eval(row[3])
            ) for row in data
        }

async def get_setups() -> List[SetupRecommendation]:
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await db.execute("SELECT * FROM setups")
        data = await rows.fetchall()
        return [
            SetupRecommendation(
                unit_type=row[1],
                officers=eval(row[2]),
                skills=eval(row[3]),
                comment=row[4]
            ) for row in data
        ]

async def add_officer(code: str, name: str, description: str, best_for: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO officers VALUES (?, ?, ?, ?)",
            (code, name, description, best_for)
        )
        await db.commit()

async def add_skill(code: str, name: str, description: str, best_for: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO skills VALUES (?, ?, ?, ?)",
            (code, name, description, best_for)
        )
        await db.commit()

async def add_setup(unit_type: str, officers: str, skills: str, comment: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO setups (unit_type, officers, skills, comment) VALUES (?, ?, ?, ?)",
            (unit_type, officers, skills, comment)
        )
        await db.commit()

async def find_best_setup(unit_type: UnitType, owned_officers: List[str], owned_skills: List[str]) -> SetupRecommendation:
    setups = await get_setups()
    best = None
    best_score = -1
    for s in setups:
        if s.unit_type != unit_type: continue
        officers_match = len(set(s.officers) & set(owned_officers))
        skills_match = len(set(s.skills) & set(owned_skills))
        score = officers_match * 2 + skills_match
        if score > best_score:
            best_score = score
            best = s
    if best is None:
        raise ValueError("Нет сетапов для данного типа юнита")
    return best
