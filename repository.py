from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import ASCENDING
from pymongo.errors import PyMongoError

from db import get_collection

def ensure_indexes():
    coll = get_collection()
    coll.create_index([("name", ASCENDING)])
    coll.create_index([("email", ASCENDING)])

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email and len(email) <= 254

def parse_object_id(id_str: str) -> Optional[ObjectId]:
    try:
        return ObjectId(id_str)
    except Exception:
        return None

def create_person(doc: Dict[str, Any]) -> Optional[ObjectId]:
    coll = get_collection()
    try:
        res = coll.insert_one(doc)
        return res.inserted_id
    except PyMongoError as e:
        print(f"Error inserting: {e}")
        return None

def list_people(filter_q: Dict[str, Any] = None, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
    coll = get_collection()
    q = filter_q or {}
    cursor = coll.find(q).skip(skip).limit(limit)
    return list(cursor)

def get_person(person_id: str) -> Optional[Dict[str, Any]]:
    coll = get_collection()
    oid = parse_object_id(person_id)
    if oid is None:
        return None
    return coll.find_one({"_id": oid})

def update_person(person_id: str, updates: Dict[str, Any]) -> bool:
    coll = get_collection()
    oid = parse_object_id(person_id)
    if oid is None:
        return False
    try:
        res = coll.update_one({"_id": oid}, {"$set": updates})
        return res.matched_count > 0
    except PyMongoError as e:
        print(f"Error updating: {e}")
        return False

def delete_person(person_id: str) -> bool:
    coll = get_collection()
    oid = parse_object_id(person_id)
    if oid is None:
        return False
    try:
        res = coll.delete_one({"_id": oid})
        return res.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting: {e}")
        return False
