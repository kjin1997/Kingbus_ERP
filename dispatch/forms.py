from django import forms 
from django.db import models

from .models import DispatchOrder, DispatchOrderConnect, DispatchRegularlyData

class RegularlyDataForm(forms.ModelForm):
    class Meta:
        model = DispatchRegularlyData
        fields = [
            'references',
            'departure',
            'arrival',
            # 'departure_time',
            # 'arrival_time',
            # 'bus_type',
            # 'bus_cnt',
            # 'price',
            # 'driver_allowance',
            'number1',
            'number2',
            # 'customer',
            # 'customer_phone',
            # 'contract_start_date',
            # 'contract_end_date',
            'work_type',
            'route',
            'location',
            'detailed_route',
            'maplink',
            'use',
            ]

class OrderForm(forms.ModelForm):
    class Meta:
        model = DispatchOrder
        fields = [
            'operation_type',
            'references',
            'departure',
            'arrival',
            'bus_type',
            'bus_cnt',
            'contract_status',
            'customer',
            'customer_phone',
            'bill_place',
            'ticketing_info',
            'order_type',
            'operating_company',
            'reservation_company',
            'driver_lease',
            'vehicle_lease',
            ]
        
        # widgets = {
        #     'departure_date': forms.DateInput(format='%Y-%m-%d H:i', attrs={'type':'datetime-local'}),
        #     'arrival_date': forms.DateInput(format='%Y-%m-%d H:i', attrs={'type':'datetime-local'}),
        # }
        
'''
class OrderForm(forms.ModelForm):
    class Meta:
        model = DispatchOrder
        fields = [ 
            'bus_cnt', 
            'driver_allowance',
            'price', 
            'way',
            'purpose',
            'bus_type',
            'reference',
            'departure',
            'arrival',
            'stopover',
            'route_name',
            'departure_date',
            'arrival_date',
            ]

        widgets = {
            'departure_date': forms.DateInput(format='%Y-%m-%d H:i', attrs={'type':'datetime-local'}),
            'arrival_date': forms.DateInput(format='%Y-%m-%d H:i', attrs={'type':'datetime-local'}),
        }
'''

class ConnectForm(forms.ModelForm):
    class Meta:
        model = DispatchOrderConnect
        fields = [
            'bus_id',
            'driver_id',
            'departure_date',
            'arrival_date',
        ]
'''
class OrderForm(forms.Form):
    bus_cnt = forms.IntegerField(label="버스대수")
    price = forms.IntegerField(label="가격")
    kinds = forms.CharField(label="왕복or편도")
    purpose = forms.CharField(label="용도")
    bus_type = forms.CharField(label="버스종류")
    requirements = forms.CharField(label="요구사항")
    people_num = forms.IntegerField(label="탑승인원")
    pay_type = forms.CharField(label="카드or현금")


    def save(self, commit=True):
        self.instance = DispatchOrder(**self.cleaned_data)
        if commit:
            self.instance.save()
        return self.instance
'''