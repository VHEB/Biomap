from django.http import HttpResponse

def index(request):
    return HttpResponse("Olá, bem-vindo ao BioMap!")