import os
from fastapi import FastAPI, Depends
from routers import transactions, messages, wallets, authentications, friends

from fastapi.middleware.cors import CORSMiddleware
from jwt_utils import get_current_user

FRONT_END_LOCALHOST_URL = "http://localhost:3000"
FRONTEND_URL_8000 = "http://localhost:8000"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_END_LOCALHOST_URL, FRONTEND_URL_8000],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Bitcoin Threshold Wallet"}

# Include API routes with authentication
app.include_router(authentications.router)  # No authentication for login routes
app.include_router(transactions.router, dependencies=[Depends(get_current_user)])
app.include_router(wallets.router, dependencies=[Depends(get_current_user)])
app.include_router(friends.router, dependencies=[Depends(get_current_user)])

@app.on_event("startup")
async def open_swagger_ui():
    import asyncio
    await asyncio.sleep(1)  # Small delay to ensure server starts
    # webbrowser.open("http://127.0.0.1:8000/docs")  # Adjust URL if needed

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Bitcoin Threshold Wallet API')
    parser.add_argument('--other', type=bool, default=False, help='Run another server')
    # Parse arguments
    args = parser.parse_args()
    if not args.other:
        os.environ['USER_NUM'] = 'user1'
        port = 6060
    else:
        os.environ['USER_NUM'] = 'user2'
        port = 7070
    
    # Run with the specified or default port
    uvicorn.run(app, host="0.0.0.0", port=port)
