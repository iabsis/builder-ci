from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class ExampleIndex(TemplateView):
    template_name = "index.html"


class ExampleButtons(TemplateView):
    template_name = "buttons.html"


class ExampleCards(TemplateView):
    template_name = "cards.html"


class ExampleUtilitiesColor(TemplateView):
    template_name = "utilities-color.html"


class ExampleUtilitiesBorder(TemplateView):
    template_name = "utilities-border.html"


class ExampleUtilitiesAnimation(TemplateView):
    template_name = "utilities-animation.html"


class ExampleUtilitiesOther(TemplateView):
    template_name = "utilities-other.html"


class ExampleCharts(TemplateView):
    template_name = "charts.html"


class ExampleTables(TemplateView):
    template_name = "tables.html"


class ExampleForm(TemplateView):
    template_name = "form.html"
