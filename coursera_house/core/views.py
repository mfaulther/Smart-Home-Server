from django.urls import reverse_lazy
from django.views.generic import FormView


from .models import Setting
from .form import ControllerForm

import json


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        with open('context.data', 'r') as f:
            data = json.loads(f.read())
        context['data'] = data
        return context

    def get_initial(self):
        return {}

    def form_valid(self, form):
        bedroom_target_temperature = form.data.get('bedroom_target_temperature')
        hot_water_target_temperature = form.data.get('hot_water_target_temperature')

        bedroom_temp_setting = Setting.objects.get(controller_name='bedroom_target_temperature')
        bedroom_temp_setting.value = bedroom_target_temperature
        bedroom_temp_setting.save()

        hot_water_temp_setting = Setting.objects.get(controller_name='hot_water_target_temperature')
        hot_water_temp_setting.value = hot_water_target_temperature
        hot_water_temp_setting.save()

        return super(ControllerView, self).form_valid(form)





