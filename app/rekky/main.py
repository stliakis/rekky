import os
from dotenv import load_dotenv
from fastapi import FastAPI

from rekky.settings import get_settings
from rekky.views.events import events
from rekky.views.items import items
from rekky.views.recommendations import recommendations

load_dotenv()

os.environ["OPENAI_API_KEY"] = get_settings().OPENAI_API_KEY

app = FastAPI(redoc_url="/docs", docs_url="/docs/swagger")

app.include_router(items.router)
app.include_router(events.router)
app.include_router(recommendations.router)
