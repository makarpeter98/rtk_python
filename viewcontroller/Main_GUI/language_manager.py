import json

class LanguageManager:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def t(self, *keys):
        """Hierarchikus kulcsok lekérése: t('measurement_view', 'fields', 'Latitude')"""
        ref = self.data
        for k in keys:
            ref = ref[k]
        return ref
