from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class ExampleIndex(TemplateView):
    template_name = "example/index.html"


class ExampleButtons(TemplateView):
    template_name = "example/buttons.html"


class ExampleCards(TemplateView):
    template_name = "example/cards.html"


class ExampleUtilitiesColor(TemplateView):
    template_name = "example/utilities-color.html"


class ExampleUtilitiesBorder(TemplateView):
    template_name = "example/utilities-border.html"


class ExampleUtilitiesAnimation(TemplateView):
    template_name = "example/utilities-animation.html"


class ExampleUtilitiesOther(TemplateView):
    template_name = "example/utilities-other.html"


class ExampleCharts(TemplateView):
    template_name = "example/charts.html"


class ExampleTables(TemplateView):
    template_name = "example/tables.html"


class ExampleForm(TemplateView):
    template_name = "example/form.html"
