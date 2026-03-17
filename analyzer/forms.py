from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class KazakhUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Пайдаланушы аты",
        help_text="Міндетті өріс. 150 таңбаға дейін. Әріптер мен сандарды қолданыңыз.",
        error_messages={
            "required": "Пайдаланушы атын енгізіңіз.",
            "unique": "Бұл пайдаланушы аты бұрыннан бар.",
        },
    )

    password1 = forms.CharField(
        label="Құпиясөз",
        widget=forms.PasswordInput,
        help_text=(
            "Құпиясөз кемінде 8 таңбадан тұруы керек.<br>"
            "Тек сандардан тұрмауы керек.<br>"
            "Өте қарапайым болмауы керек."
        ),
        error_messages={"required": "Құпиясөзді енгізіңіз."},
    )

    password2 = forms.CharField(
        label="Құпиясөзді растау",
        widget=forms.PasswordInput,
        help_text="Құпиясөзді қайта енгізіңіз.",
        error_messages={"required": "Құпиясөзді қайта енгізіңіз."},
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Құпиясөздер сәйкес келмейді.")

        return password2
