import webbrowser
from fastapi import FastAPI
from routers import transactions, messages, wallets
import os
from fastapi.middleware.cors import CORSMiddleware

FRONT_END_LOCALHOST_URL = "http://localhost:3000"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_END_LOCALHOST_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Bitcoin Threshold Wallet"}

# Include API routes
app.include_router(transactions.router, prefix="/transactions")
app.include_router(messages.router, prefix="/messages")
app.include_router(wallets.router, prefix="/wallets")

@app.on_event("startup")
async def open_swagger_ui():
    import asyncio
    await asyncio.sleep(1)  # Small delay to ensure server starts
    webbrowser.open("http://127.0.0.1:8000/docs")  # Adjust URL if needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
