from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Area, Curso, Matricula


class CorreoUnicoMixin:
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        usuarios = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            usuarios = usuarios.exclude(pk=self.instance.pk)
        if usuarios.exists():
            raise forms.ValidationError('Este correo ya pertenece a otra cuenta.')
        return email


class RegistroForm(CorreoUnicoMixin, UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class PerfilForm(CorreoUnicoMixin, forms.ModelForm):
    email = forms.EmailField(label='Correo electrónico', required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'horas', 'cupos', 'modalidad', 'fecha_inicio', 'area', 'competencias']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'competencias': forms.CheckboxSelectMultiple(),
        }
        help_texts = {'horas': 'Entre 4 y 200 horas.', 'cupos': 'Entre 5 y 60 participantes.',
                      'area': 'Opcional. El curso se conserva si el área se elimina.',
                      'competencias': 'Selecciona hasta cinco competencias.'}

    def clean_competencias(self):
        competencias = self.cleaned_data['competencias']
        if len(competencias) > 5:
            raise forms.ValidationError('Puedes seleccionar un máximo de cinco competencias.')
        return competencias


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre']


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['empresa']
        help_texts = {'empresa': 'Nombre de la empresa a la que perteneces.'}
