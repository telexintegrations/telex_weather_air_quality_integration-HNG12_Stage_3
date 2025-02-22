from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    message = {
        "info": "Welcome to Weather an air quality Monitor",
        "status": "success"
    }
    return message, 200


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)