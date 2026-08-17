from django.shortcuts import render

# Create your views here.
def portfolio_home(request):
    context = {
        'nombre': 'Franco Morales',
        'profesion': 'Desarrollador Full Stack',
        'anios_experiencia': '8'
    }

    return render(request, "home.html", context)

def portfolio_mis_servicios(request):
    context = {
        'servicios': [
            { 'nombre': 'Sitios web', 'descripcion': 'Diseño de sitios web.' },
            { 
                'nombre': 'Arquitectura', 
                'descripcion': 'Se diseñan arquitecturas solidas para software.' 
            },
        ]
    }
    return render(request, "servicios.html", context)