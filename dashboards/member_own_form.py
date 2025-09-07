
    def clean_my_title(self):
        title = self.cleaned_data.get("my_title")
        if not title:
            raise forms.ValidationError("Titel is verplicht.")
        return title
