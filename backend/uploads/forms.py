# uploads/forms.py
from django import forms
from .models import File


# ModelForm is a special type of form in Django that knows how to connect to a database model
class FileUploadForm(forms.ModelForm):

    # Without meta django will not know which model to use and which fields to include in the form
    class Meta:
        # tells Django: “This form creates or edits User objects in the database
        model = File
        # tells Django: Only show these fields in the HTML form. Don’t show all fields from the model
        fields = ["file"]  # user only selects the file
