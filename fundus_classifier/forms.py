from django.forms import ModelForm
from models import *

class UploadForm(ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']
    def __init__(self , *args , **kwargs):
        super(ModelForm , self).__init__(*args, **kwargs)
        self.fields['file'].required = False
