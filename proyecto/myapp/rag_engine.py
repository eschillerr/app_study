# rag_engine.py
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")


def load_multiple_pdfs():
    """Carga múltiples archivos PDF desde la base de datos"""
    # Import aquí para evitar referencias circulares
    from .models import Document

    all_documents = []
    documentos = Document.objects.all()

    if not documentos.exists():
        return []

    for documento in documentos:
        try:
            loader = PyPDFLoader(documento.file.path)
            pages = loader.load()
            for page in pages:
                page.metadata['source_file'] = os.path.basename(documento.file.name)
            all_documents.extend(pages)
        except Exception as e:
            print(f"Error cargando {documento.file.name}: {e}")
            continue
    return all_documents


def generate_questions(user_request):
    """
    Genera preguntas basadas en los documentos cargados
    user_request: El tipo de preguntas que el usuario quiere (ej: "Crea 5 preguntas de opción múltiple")
    """
    # Cargar y procesar documentos
    documents = load_multiple_pdfs()
    if not documents:
        raise ValueError("No hay PDFs cargados")

    # Dividir documentos en chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    # Crear embeddings y vectorstore
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Buscar los chunks más relevantes para el contexto
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.invoke(user_request)

    # Crear contexto con los documentos relevantes
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Prompt para generar preguntas
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente especializado en crear preguntas de estudio basadas en documentos académicos.
Tu objetivo es ayudar a los estudiantes a estudiar generando preguntas útiles y bien estructuradas.

Cuando generes preguntas:
- Asegúrate de que sean claras y específicas
- Basate exclusivamente en el contenido proporcionado
- Para preguntas de opción múltiple, incluye 4 opciones y marca la correcta
- Para preguntas abiertas, proporciona la respuesta esperada
- Numera las preguntas claramente

Contexto del documento:
{context}"""),
        ("human", "{question}")
    ])

    # Crear el LLM
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    # Generar respuesta
    chain = prompt | llm
    result = chain.invoke({
        "context": context,
        "question": user_request
    })

    # Extraer fuentes
    sources = list(set([doc.metadata.get('source_file', 'Unknown') for doc in relevant_docs]))

    return {
        'answer': result.content,
        'sources': sources
    }
