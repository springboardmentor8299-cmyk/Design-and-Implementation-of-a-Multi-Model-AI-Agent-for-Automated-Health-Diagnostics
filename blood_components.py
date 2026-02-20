class BloodComponents:
    def __init__(self, hemoglobin=None, glucose=None, cholesterol=None, rbc=None, wbc=None):
        self.hemoglobin = hemoglobin
        self.glucose = glucose
        self.cholesterol = cholesterol
        self.rbc = rbc
        self.wbc = wbc

    def to_dict(self):
        return {
            "hemoglobin": self.hemoglobin,
            "glucose": self.glucose,
            "cholesterol": self.cholesterol,
            "RBC": self.rbc,
            "WBC": self.wbc
        }