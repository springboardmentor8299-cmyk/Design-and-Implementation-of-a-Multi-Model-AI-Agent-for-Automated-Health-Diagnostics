class DataValidator:
    def validate(self, data):
        validated = {}
        for key, value in data.items():
            if isinstance(value, (int, float)) and value >= 0:
                validated[key] = value
        return validated
    
    def standardize(self, data):
        return data
