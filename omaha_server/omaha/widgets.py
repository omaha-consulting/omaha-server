from tinymce.widgets import TinyMCE


class CustomTinyMCE(TinyMCE):
    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs)
