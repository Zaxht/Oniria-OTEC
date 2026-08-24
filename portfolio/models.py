from django.db import models

# Create your models here.
class Proyecto():
    def __init__(self, id, titulo, descripcion, tecnologia):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.tecnologia = tecnologia

def proyectos():
    lista_proyectos = [
        Proyecto(1, "Aplicacion web", "Una aplicacion bonita.", "django"),
        Proyecto(2, "Deploys", "Deployamos aplicciones con pipelines", "Docker y K8S"),
        Proyecto(3, "Tarot", "Se lee el tarot", "La luna y el universo")
    ]
    return lista_proyectos