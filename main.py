import webbrowser
from fastapi import FastAPI
from routers import transactions, messages

app = FastAPI()

# Include API routes
app.include_router(transactions.router, prefix="/transactions")
app.include_router(messages.router, prefix="/messages")

@app.on_event("startup")
async def open_swagger_ui():
    import asyncio
    await asyncio.sleep(1)  # Small delay to ensure server starts
    webbrowser.open("http://127.0.0.1:8000/docs")  # Adjust URL if needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
