from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from pydantic import BaseModel, EmailStr
from typing import List
import httpx

app = FastAPI()

class Profile(BaseModel):
    description: str
    skills: List[str]


class Job(BaseModel):
    title: str
    profile: str
    description: str
    skills: List[str]
    email: str

    #https://n8n.bambyno.xyz/webhook-test/lettre


# Montage des fichiers statiques (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration de Jinja2 pour rendre des templates HTML
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/profile")
async def receive_profile(profile: Profile):
    # Traitement côté serveur
    print(profile.dict())  # Pour debug dans la console

    return JSONResponse(content={
        "message": "Profil reçu avec succès",
        "data": profile.dict()
    })



@app.post("/job")
async def receive_job(job: Job):
    print(job.dict())  # Affiche l'objet reçu dans la console

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://n8n.bambyno.xyz/webhook/lettre",
                json=job.dict(),
                timeout=10.0  # facultatif mais conseillé
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPError as exc:
            return JSONResponse(
                status_code=500,
                content={"message": "Erreur lors de l'appel à n8n", "detail": str(exc)}
            )

    print(result)
    return JSONResponse(content={
        "message": "Job enrichi reçu avec succès",
        "data": result
    })


@app.get("/hello", response_class=HTMLResponse)
async def hello():
    return "<div>👋 Bonjour depuis FastAPI + HTMX !</div>"
