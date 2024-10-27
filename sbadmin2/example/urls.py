from django.urls import include, path
from . import views

urlpatterns = [
    path('index/', views.ExampleIndex.as_view(), name='example_index'),
    path('buttons/', views.ExampleButtons.as_view(), name='example_buttons'),
    path('cards/', views.ExampleCards.as_view(), name='example_cards'),
    path('utilities-color/', views.ExampleUtilitiesColor.as_view(),
         name='example_utilities_color'),
    path('utilities-border/', views.ExampleUtilitiesBorder.as_view(),
         name='example_utilities_border'),
    path('utilities-animation/', views.ExampleUtilitiesAnimation.as_view(),
         name='example_utilities_animation'),
    path('utilities-other/', views.ExampleUtilitiesOther.as_view(),
         name='example_utilities_other'),
    path('charts/', views.ExampleCharts.as_view(),
         name='example_charts'),
    path('tables/', views.ExampleTables.as_view(),
         name='example_tables'),
    path('form/', views.ExampleForm.as_view(),
         name='example_form'),
]
