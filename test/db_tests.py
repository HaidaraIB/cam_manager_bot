import os
import sys
from dotenv import load_dotenv
import asyncio
from unittest.mock import AsyncMock, patch
from telegram import Update, User, Chat
from telegram.ext import ContextTypes

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models

async def main():
    load_dotenv()
    models.create_tables()
    cam = models.Camera.get_by(attr="id", val=1)
    print(cam.photos)


asyncio.run(main())
