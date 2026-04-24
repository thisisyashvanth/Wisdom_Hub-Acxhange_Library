from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.user_api import router as user_router
from api.auth_api import router as auth_router
from api.book_api import router as book_router
from api.request_api import router as request_router
from api.excel_api import router as excel_router
from mangum import Mangum


app = FastAPI(title="Wisdom Hub - Acxhange Library")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Add CDN Deployed Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(request_router)
app.include_router(excel_router)


@app.get("/setup")
def setup():
    return {"message": "Run: core/dynamo_tables.py, success."}


handler = Mangum(app)