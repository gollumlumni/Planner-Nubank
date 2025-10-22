from dotenv import load_dotenv
from langchain_core.globals import set_debug
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Type, Optional, List, Dict
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pprint import pprint

# carregando ambiente
load_dotenv()

# modo debug
set_debug(True)

# inicializando rag
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

carregadores = [
    PyPDFLoader("./BNCC-Documento-Final.pdf"),
]

documentos = []
for carregador in carregadores:
    documentos.extend(carregador.load())

quebrador = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
textos = quebrador.split_documents(documentos)

# indexando os textos
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(textos, embeddings)
qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Define o schema da resposta usando Pydantic
class EtapaAula(BaseModel):
    nome: str = Field(description="Nome da etapa da aula")
    tempo: str = Field(description="Tempo estimado para a etapa")
    atividades: List[str] = Field(description="Lista de atividades da etapa")

class Metodologia(BaseModel):
    metodologias_sugeridas: List[str] = Field(description="Lista das metodologias apropriadas")
    justificativa: str = Field(description="Justificativa para a escolha das metodologias")

class EstruturaAula(BaseModel):
    tempo_total: str = Field(description="Tempo total da aula")
    etapas: List[EtapaAula] = Field(description="Lista das etapas da aula")

class Avaliacao(BaseModel):
    tipos: List[str] = Field(description="Tipos de avaliação")
    criterios: List[str] = Field(description="Critérios de avaliação")

class PlanoAula(BaseModel):
    habilidades_bncc: List[str] = Field(description="Habilidades da BNCC relacionadas")
    objetivos_aula: List[str] = Field(description="Objetivos específicos da aula")
    metodologia: Metodologia = Field(description="Metodologias e justificativas")
    materiais_necessarios: List[str] = Field(description="Lista de materiais necessários")
    estrutura_aula: EstruturaAula = Field(description="Estrutura detalhada da aula")
    avaliacao: Avaliacao = Field(description="Formas e critérios de avaliação")
    para_saber_mais: List[str] = Field(description="Informações complementares e curiosidades")

# modelo de dados para input do planner
class PlanoAulaInput(BaseModel):
    tema_conteudo: str = Field(description="O tema e conteúdo da aula")
    publico: str = Field(description="Público-alvo (ex: 6º ano, 1ª série do ensino médio, etc.)")
    habilidades: Optional[str] = Field(None, description="Habilidades específicas da BNCC (opcional)")
    objetivos: Optional[str] = Field(None, description="Objetivos específicos da aula (opcional)")
    tempo_aula: str = Field(description="Tempo disponível para a aula ou quantidade de aulas")
    recursos_didaticos: Optional[str] = Field(None, description="Recursos didáticos disponíveis (opcional)")

# ferramenta de busca BNCC
class BuscarBNCC(BaseTool):
    name: str = "BuscarBNCC"
    description: str = (
        """Use esta ferramenta para procurar as habilidades da BNCC de acordo com
        o tema, conteúdo e público-alvo (ano/série)."""
    )

    class Query(BaseModel):
        query: str = Field(description="O conteúdo, tema e público-alvo que deve ser pesquisado na BNCC.")

    args_schema: Type[BaseModel] = Query

    def _run(self, query: str) -> str:
        resposta = qa_chain.invoke({"query": query})
        return resposta['result']

# parser e template
parser = JsonOutputParser(pydantic_object=PlanoAula)

template_plano = PromptTemplate(
    template="""Crie um plano de aula completo e detalhado sobre o tema "{tema_conteudo}", para alunos do {publico}, considerando {tempo_aula}.

Habilidades BNCC encontradas:
{habilidades_bncc}

{objetivos_info}
{recursos_info}

Baseie-se nas seguintes metodologias disponíveis:
- Aplicação de exercícios
- Aula expositiva
- Dramatização
- Estudo de caso
- Estudo dirigido
- Estudo de texto
- Mapa conceitual
- Painel
- Pesquisa de campo
- Seminário
- Solução de problemas

{format_instructions}
""",
    input_variables=["tema_conteudo", "publico", "tempo_aula", "habilidades_bncc", "objetivos_info", "recursos_info"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

buscar_bncc = BuscarBNCC()

class PlannerAgent:
    def __init__(self):
        model = ChatOpenAI(model='gpt-4o', temperature=0.3)
        tools = [
            Tool(
                name=buscar_bncc.name,
                func=buscar_bncc.run,
                description=buscar_bncc.description,
            )
        ]

        self.agente = create_react_agent(
            model=model,
            tools=tools,
            name="PlannerEducacional"
        )

        # cadeia estruturada
        self.cadeia_estruturada = template_plano | model | parser

    def buscar_habilidades_bncc(self, tema: str, publico: str) -> str:
        """Busca habilidades da BNCC usando a ferramenta"""
        return buscar_bncc.run(f"Quais são as habilidades da BNCC relacionadas ao tema '{tema}' para alunos do {publico}?")

    def criar_plano_aula(self, dados: PlanoAulaInput) -> PlanoAula:
        # buscar habilidades da BNCC primeiro
        habilidades_bncc = self.buscar_habilidades_bncc(dados.tema_conteudo, dados.publico)
        
        # preparar informações opcionais
        objetivos_info = f"Objetivos específicos: {dados.objetivos}" if dados.objetivos else ""
        recursos_info = f"Recursos disponíveis: {dados.recursos_didaticos}" if dados.recursos_didaticos else ""
        
        # usar a cadeia estruturada para gerar o plano
        resultado = self.cadeia_estruturada.invoke({
            "tema_conteudo": dados.tema_conteudo,
            "publico": dados.publico,
            "tempo_aula": dados.tempo_aula,
            "habilidades_bncc": habilidades_bncc,
            "objetivos_info": objetivos_info,
            "recursos_info": recursos_info
        })

        return resultado

# exemplo de uso direto com variáveis
if __name__ == "__main__":
    # definir variáveis
    tema_conteudo = "Prismas e pirâmides"
    publico = "9º ano do Ensino Fundamental"
    tempo_aula = "2 aulas de 50 minutos cada"
    objetivos = "Fazer com que os alunos identifiquem e calculem área e volume de prismas e pirâmides"
    recursos_didaticos = "Quadro, projetor, material concreto (sólidos geométricos)"
    
    dados = PlanoAulaInput(
        tema_conteudo=tema_conteudo,
        publico=publico,
        objetivos=objetivos,
        tempo_aula=tempo_aula,
        recursos_didaticos=recursos_didaticos
    )
    
    planner = PlannerAgent()
    resultado = planner.criar_plano_aula(dados)
    
    pprint(resultado)