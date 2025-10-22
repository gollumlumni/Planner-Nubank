from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from planner import PlannerAgent, PlanoAulaInput

app = FastAPI()
planner = PlannerAgent()

# habilita acesso do Next.js (localhost:3000, por exemplo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, coloque o domínio do site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GerarRequest(BaseModel):
    tema_conteudo: str
    publico: str
    tempo_aula: str
    objetivos: str | None = None
    recursos_didaticos: str | None = None

@app.post("/gerar")
def gerar_plano(req: GerarRequest):
    dados = PlanoAulaInput(
        tema_conteudo=req.tema_conteudo,
        publico=req.publico,
        tempo_aula=req.tempo_aula,
        objetivos=req.objetivos,
        recursos_didaticos=req.recursos_didaticos
    )
    resultado = planner.criar_plano_aula(dados)
    return resultado
