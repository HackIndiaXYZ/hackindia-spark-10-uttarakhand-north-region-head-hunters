from fastapi import FastAPI

app = FastAPI(title="CHITRAGUPT API")


@app.get("/")
def root():
    return {"message": "CHITRAGUPT API is running"}