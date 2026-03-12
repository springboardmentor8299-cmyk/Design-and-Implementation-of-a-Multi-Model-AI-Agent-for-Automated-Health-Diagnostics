"""
Data Validation & Standardization Module
Validates and standardizes extracted blood parameter data
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class UnitConverter:
    """Converts between different measurement units"""
    
    # Conversion factors to standard units
    CONVERSIONS = {
        "hemoglobin": {
            "g/dl": 1.0,
            "g/100ml": 1.0,
            "mmol/l": 0.06206,  # To g/dL
        },
        "glucose": {
            "mg/dl": 1.0,
            "mmol/l": 18.0182,  # To mg/dL
        },
        "cholesterol": {
            "mg/dl": 1.0,
            "mmol/l": 38.67,  # To mg/dL
        },
        "triglycerides": {
            "mg/dl": 1.0,
            "mmol/l": 88.57,  # To mg/dL
        },
    }
    
    @staticmethod
    def convert(value: float, parameter: str, from_unit: str, to_unit: str = None) -> Tuple[float, str]:
        from_unit = from_unit.lower().strip()
        
        # If unit is already standard or recognized, return as-is
        return value, from_unit


class DataValidator:
    """Validates extracted blood parameters"""
    
    def __init__(self, reference_ranges_path: Optional[Path] = None):
        self.reference_ranges = self._load_reference_ranges(reference_ranges_path)
        self.logger = logging.getLogger(__name__)
    
    def _load_reference_ranges(self, reference_ranges_path: Optional[Path]) -> Dict[str, Any]:
        """Load reference ranges from JSON file"""
        try:
            if reference_ranges_path and Path(reference_ranges_path).exists():
                with open(reference_ranges_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load reference ranges: {str(e)}")
        
        # Return minimal default ranges if file not found
        return {
            "blood_parameters": {
                "hemoglobin": {
                    "reference_ranges": {
                        "male": {"min": 13.5, "max": 17.5},
                        "female": {"min": 12.0, "max": 15.5}
                    }
                }
            }
        }
    
    def validate_parameter(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        param_name = parameter.get("parameter")
        value = parameter.get("value")
        
        if not param_name or value is None:
            return {
                "valid": False,
                "error": "Missing required fields (parameter, value)",
                "parameter": param_name
            }
        
        if not isinstance(value, (int, float)):
            return {
                "valid": False,
                "error": f"Value is not numeric: {value}",
                "parameter": param_name
            }
        
        if value < 0:
            return {
                "valid": False,
                "error": f"Negative value not plausible: {value}",
                "parameter": param_name
            }
        
        return {
            "valid": True,
            "parameter": param_name
        }
    
    def validate_dataset(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        parameters = extracted_data.get("parameters", [])
        
        validation_results = []
        valid_count = 0
        invalid_count = 0
        
        for param in parameters:
            result = self.validate_parameter(param)
            validation_results.append(result)
            
            if result.get("valid"):
                valid_count += 1
            else:
                invalid_count += 1
        
        min_required = 5
        dataset_valid = valid_count >= min_required
        
        return {
            "dataset_valid": dataset_valid,
            "valid_parameters": valid_count,
            "invalid_parameters": invalid_count,
            "total_parameters": len(parameters),
            "details": validation_results,
            "error": None if dataset_valid else f"Minimum {min_required} parameters required"
        }
    
    def check_for_missing_parameters(self, parameters: List[Dict[str, Any]]) -> List[str]:
        extracted_params = {p["parameter"] for p in parameters}
        critical_params = {"hemoglobin", "glucose", "total_cholesterol"}
        missing = critical_params - extracted_params
        return list(missing)


class DataStandardizer:
    """Standardizes data format and structure"""
    
    @staticmethod
    def standardize_parameters(
        parameters: List[Dict[str, Any]], 
        gender: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        standardized = []
        
        for param in parameters:
            standardized_param = {
                "parameter": param.get("parameter"),
                "value": float(param.get("value", 0)),
                "unit": param.get("unit", "").strip(),
                "raw_name": param.get("raw_name", ""),
                "timestamp": None,
                "source": param.get("source_line", "")
            }
            standardized.append(standardized_param)
        
        return standardized
    
    @staticmethod
    def create_report_summary(
        raw_parameters: List[Dict[str, Any]],
        validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "total_parameters_extracted": len(raw_parameters),
            "valid_parameters": validation_report.get("valid_parameters"),
            "invalid_parameters": validation_report.get("invalid_parameters"),
            "dataset_valid": validation_report.get("dataset_valid"),
            "parameters": raw_parameters,
            "validation_details": validation_report.get("details", [])
        }
