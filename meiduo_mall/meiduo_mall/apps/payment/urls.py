from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns=[
    url(r'^orders/(?P<order_id>\d+)/payment/$',views.PaymentView.as_view()),

]

