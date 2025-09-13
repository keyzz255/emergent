from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import requests
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# DramaBox API Configuration
DRAMABOX_TOKEN_URL = "https://dramabox-token.vercel.app/token"
DRAMABOX_BASE_URL = "https://sapi.dramaboxdb.com/drama-box"

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class SearchRequest(BaseModel):
    keyword: str

class StreamRequest(BaseModel):
    book_id: str
    episode: int = 1

# DramaBox API Helper Functions
async def get_dramabox_token():
    """Get authentication token from DramaBox API"""
    try:
        response = requests.get(DRAMABOX_TOKEN_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get DramaBox token: {e}")
        raise HTTPException(status_code=500, detail="Failed to get authentication token")

def get_dramabox_headers(token_data):
    """Generate headers for DramaBox API requests"""
    return {
        "User-Agent": "okhttp/4.10.0",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
        "tn": f"Bearer {token_data['token']}",
        "version": "430",
        "vn": "4.3.0",
        "cid": "DRA1000042",
        "package-name": "com.storymatrix.drama",
        "apn": "1",
        "device-id": token_data['deviceid'],
        "language": "in",
        "current-language": "in",
        "p": "43",
        "time-zone": "+0800",
        "content-type": "application/json; charset=UTF-8"
    }

# DramaBox API Routes
@api_router.get("/dramas/latest")
async def get_latest_dramas(page: int = 1):
    """Get latest dramas from DramaBox"""
    try:
        token_data = await get_dramabox_token()
        headers = get_dramabox_headers(token_data)
        
        url = f"{DRAMABOX_BASE_URL}/he001/theater"
        data = {
            "newChannelStyle": 1,
            "isNeedRank": 1,
            "pageNo": page,
            "index": 1,
            "channelId": 43
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get("data") and result["data"].get("newTheaterList"):
            return {
                "success": True,
                "data": result["data"]["newTheaterList"]["records"],
                "page": page
            }
        else:
            return {"success": False, "data": [], "message": "No data found"}
            
    except Exception as e:
        logger.error(f"Failed to get latest dramas: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch latest dramas")

@api_router.post("/dramas/search")
async def search_dramas(request: SearchRequest):
    """Search dramas by keyword"""
    try:
        token_data = await get_dramabox_token()
        headers = get_dramabox_headers(token_data)
        
        url = f"{DRAMABOX_BASE_URL}/search/suggest"
        data = {"keyword": request.keyword}
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get("data") and result["data"].get("suggestList"):
            return {
                "success": True,
                "data": result["data"]["suggestList"],
                "keyword": request.keyword
            }
        else:
            return {"success": False, "data": [], "message": "No results found"}
            
    except Exception as e:
        logger.error(f"Failed to search dramas: {e}")
        raise HTTPException(status_code=500, detail="Failed to search dramas")

@api_router.post("/dramas/stream")
async def get_stream_link(request: StreamRequest):
    """Get streaming link for specific drama episode"""
    try:
        token_data = await get_dramabox_token()
        headers = get_dramabox_headers(token_data)
        
        url = f"{DRAMABOX_BASE_URL}/chapterv2/batch/load"
        data = {
            "boundaryIndex": 0,
            "comingPlaySectionId": -1,
            "index": request.episode,
            "currencyPlaySource": "discover_new_rec_new",
            "needEndRecommend": 0,
            "currencyPlaySourceName": "",
            "preLoad": False,
            "rid": "",
            "pullCid": "",
            "loadDirection": 0,
            "startUpKey": "",
            "bookId": request.book_id
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get("data") and result["data"].get("chapterList"):
            chapters = result["data"]["chapterList"]
            if chapters and len(chapters) > 0:
                chapter = chapters[0]
                if chapter.get("cdnList") and len(chapter["cdnList"]) > 0:
                    return {
                        "success": True,
                        "stream_url": chapter["cdnList"][0],
                        "episode": request.episode,
                        "book_id": request.book_id,
                        "chapter_info": chapter
                    }
        
        return {"success": False, "message": "Stream link not found"}
            
    except Exception as e:
        logger.error(f"Failed to get stream link: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stream link")

# Original routes
@api_router.get("/")
async def root():
    return {"message": "DramaBox Streaming API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()