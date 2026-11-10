"""Material editorial complementario del catálogo demo; no modifica cursos del usuario."""
from .demo_catalogo import CURSOS

GUIDES = {
    CURSOS[0][0]: {'motif': 'eye', 'label': 'LOS ORÍGENES', 'steps': ['Reconocer la lucidez', 'Recorrer su historia', 'Construir una línea de tiempo'], 'sources': [('LaBerge et al. · Verificación experimental, 1981', 'https://pubmed.ncbi.nlm.nih.gov/24171230/')]},
    CURSOS[1][0]: {'motif': 'stars', 'label': 'LA EVIDENCIA', 'steps': ['Observar el laboratorio', 'Leer un estudio', 'Reconocer sus límites'], 'sources': [('Konkoly et al. · Comunicación durante REM, 2021', 'https://pubmed.ncbi.nlm.nih.gov/33607035/')]},
    CURSOS[2][0]: {'motif': 'orbit', 'label': 'LA PRÁCTICA', 'steps': ['Comparar MILD y SSILD', 'Examinar pruebas de realidad y WBTB', 'Diseñar un diario de observación'], 'sources': [('Estudio internacional de inducción · 2020', 'https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.01746/full')]},
    CURSOS[3][0]: {'motif': 'phases', 'label': 'LOS CICLOS', 'steps': ['Entender REM y no REM', 'Distinguir lucidez y control', 'Ordenar un relato de sueño'], 'sources': [('NIH · Fases y etapas del sueño', 'https://www.nhlbi.nih.gov/health/sleep/stages-of-sleep'), ('LaBerge et al. · Lucidez durante REM, 1981', 'https://pubmed.ncbi.nlm.nih.gov/24171230/')]},
    CURSOS[4][0]: {'motif': 'lotus', 'label': 'EL CUIDADO', 'steps': ['Examinar experiencias difíciles', 'Separar riesgos y mitos', 'Priorizar el descanso'], 'sources': [('Beneficios y preocupaciones · Sleep Advances, 2022', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10104404/')]},
    CURSOS[5][0]: {'motif': 'journal', 'label': 'LOS RELATOS', 'steps': ['Leer experiencias publicadas', 'Distinguir relato y evidencia', 'Crear una bitácora personal'], 'sources': [('Análisis de relatos de una comunidad · 2022', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10104404/')]},
    CURSOS[6][0]: {'motif': 'eye', 'label': 'LOS MUNDOS', 'steps': [], 'sources': []},
    CURSOS[7][0]: {'motif': 'lotus', 'label': 'LOS PAISAJES', 'steps': [], 'sources': []},
    CURSOS[8][0]: {'motif': 'journal', 'label': 'LAS HISTORIAS', 'steps': [], 'sources': []},
    CURSOS[9][0]: {'motif': 'stars', 'label': 'TU ATLAS', 'steps': [], 'sources': []},
}
DEFAULT_GUIDE = {'motif': 'lotus', 'label': 'EXPLORACIÓN ONÍRICA', 'steps': [], 'sources': []}


def guide_for(curso):
    if curso.relator.username in {'demo_relator', 'demo_relatora', 'fer@fer.com'}:
        return GUIDES.get(curso.nombre, DEFAULT_GUIDE)
    return DEFAULT_GUIDE
