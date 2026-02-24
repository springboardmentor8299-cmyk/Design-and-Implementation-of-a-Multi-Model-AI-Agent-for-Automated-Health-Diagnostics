from data_extractor import DataExtractor
from data_validator import DataValidator
from models import Model1_ParameterInterpretation, Model2_PatternRecognition, Model3_ContextualAnalysis
from synthesis_engine import SynthesisEngine
from recommendation_generator import RecommendationGenerator

class MultiModelOrchestrator:
    def __init__(self):
        self.extractor = DataExtractor()
        self.validator = DataValidator()
        self.model1 = Model1_ParameterInterpretation()
        self.model2 = Model2_PatternRecognition()
        self.model3 = Model3_ContextualAnalysis()
        self.synthesizer = SynthesisEngine()
        self.recommender = RecommendationGenerator()
    
    def process(self, file_path, file_type, context=None):
        raw_data = self.extractor.extract(file_path, file_type)
        validated_data = self.validator.validate(raw_data)
        
        interpretations = self.model1.analyze(validated_data, context)
        risks = self.model2.analyze(validated_data, context)
        contextual = self.model3.analyze(interpretations, risks, context)
        
        findings = self.synthesizer.synthesize(interpretations, risks, contextual)
        recommendations = self.recommender.generate(findings)
        
        return {
            'findings': findings,
            'recommendations': recommendations,
            'disclaimer': 'This AI interpretation is not a substitute for professional medical advice. Please consult your healthcare provider.'
        }
