from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('salary', views.SalaryList.as_view(), name='salary'),
    path('salary/<int:pk>', views.SalaryDetail.as_view(), name='salary_detail'),
    path('salary/create', views.salary_create, name='salary_create'),
    path('salary/edit', views.salary_edit, name='salary_edit'),
    path('salary/delete', views.salary_delete, name='salary_delete'),
    path('salary/remark/edit', views.remark_edit, name='remark_edit'),
    path('income', views.IncomeList.as_view(), name='income'),
    path('collect', views.CollectList.as_view(), name='collect'),
    path('collect/create', views.collect_create, name='collect_create'),
    path('regularly/collect', views.RegularlyCollectList.as_view(), name='regularly_collect'),
    path('deposit', views.DepositList.as_view(), name='deposit'),


]
