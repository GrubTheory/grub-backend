from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def ping():
    return {"message": "Grub backend is alive!"}
