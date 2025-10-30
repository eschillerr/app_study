from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document
from .rag_engine import generate_questions
import json


# Create your views here.

def home(request):
    return render(request, 'myapp/home.html')

def upload_documents(request):
    if request.method == 'POST':
        files = request.FILES.getlist('documents')

        if not files:
            return HttpResponse("No files uploaded!", status=400)

        # Guardar archivos en la base de datos
        for file in files:
            Document.objects.create(file=file, name=file.name)
            print(f"Saved: {file.name}")

        print("Documents saved successfully")

        # Redirigir a la página de quiz
        return redirect('quiz')

    return render(request, 'myapp/upload.html')

def quiz(request):
    """Vista principal del quiz donde se muestran las preguntas generadas"""
    documents = Document.objects.all()
    return render(request, 'myapp/quiz.html', {'documents': documents})

@csrf_exempt
def ask_question(request):
    """API endpoint para generar preguntas basadas en los documentos"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')

            if not question:
                return JsonResponse({'error': 'No question provided'}, status=400)

            # Generar preguntas con el RAG engine
            try:
                result = generate_questions(question)

                return JsonResponse({
                    'answer': result['answer'],
                    'sources': result['sources']
                })
            except Exception as e:
                print(f"Error generating questions: {str(e)}")
                return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)