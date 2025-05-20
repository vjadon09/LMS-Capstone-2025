from pymongo import MongoClient
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from database.db import *
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

managers_collection = db["managers"]

# Manager data
managers = [
    {
        "managerID": "MGR00023",
        "firstName": "John",
        "lastName": "Smith",
        "email": "john.smith@example.com",
        "phoneNumber": "9055550106",
        "address": {
            "streetAddress": "123 Main St",
            "city": "Toronto",
            "state": "ON",
            "country": "Canada"
        },
        "passwordHash": "MGR00023"
    },
    {
        "managerID": "MGR00024",
        "firstName": "Sarah",
        "lastName": "Taylor",
        "email": "sarah.taylor@example.com",
        "phoneNumber": "9055550107",
        "address": {
            "streetAddress": "456 Oakwood Ave",
            "city": "Ottawa",
            "state": "ON",
            "country": "Canada"
        },
        "passwordHash": "MGR00024"
    },
    {
        "managerID": "MGR00025",
        "firstName": "Michael",
        "lastName": "Brown",
        "email": "michael.brown@example.com",
        "phoneNumber": "9055550108",
        "address": {
            "streetAddress": "789 Maple St",
            "city": "Vancouver",
            "state": "BC",
            "country": "Canada"
        },
        "passwordHash": "MGR00025"
    },
    {
        "managerID": "MGR00026",
        "firstName": "Jessica",
        "lastName": "Davis",
        "email": "jessica.davis@example.com",
        "phoneNumber": "9055550109",
        "address": {
            "streetAddress": "321 Birch Rd",
            "city": "Calgary",
            "state": "AB",
            "country": "Canada"
        },
        "passwordHash": "MGR00026"
    },
    {
        "managerID": "MGR00027",
        "firstName": "David",
        "lastName": "Lee",
        "email": "david.lee@example.com",
        "phoneNumber": "9055550110",
        "address": {
            "streetAddress": "654 Pine St",
            "city": "Montreal",
            "state": "QC",
            "country": "Canada"
        },
        "passwordHash": "MGR00027"
    }
]

# Insert managers into the database
result = managers_collection.insert_many(managers)

# Print the inserted ids
print("Inserted manager IDs:", result.inserted_ids)
