import json

class LanguageManager:
    def __init__(self, languages, default_lang="en"):
        self.languages = languages
        self.current_lang = default_lang
        self.data = {}
        self.load_language(default_lang)

    def load_language(self, lang_code):
        with open(self.languages[lang_code], "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.current_lang = lang_code

    def t(self, *keys):
        ref = self.data
        for k in keys:
            ref = ref[k]
        return ref

