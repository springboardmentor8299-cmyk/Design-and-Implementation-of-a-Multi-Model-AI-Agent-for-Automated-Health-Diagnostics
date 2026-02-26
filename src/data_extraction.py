"""
Data Extraction Engine
Extracts key blood parameters from parsed report content
"""

import re
import logging
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ParameterExtractor:
    """Extracts blood parameters and values from text content"""
    
    # Common parameter names and their aliases
    PARAMETER_ALIASES = {
        "hemoglobin": ["hb", "hbg", "hemoglobin"],
        "glucose": ["fasting glucose", "blood glucose", "bg", "glucose"],
        "total_cholesterol": ["total cholesterol", "total_chol", "tc"],
        "ldl_cholesterol": ["ldl", "bad cholesterol", "ldl_chol"],
        "hdl_cholesterol": ["hdl", "good cholesterol", "hdl_chol"],
        "triglycerides": ["triglyceride", "tg"],
        "creatinine": ["creatinine", "serum creatinine"],
        "bun": ["blood urea nitrogen", "bun", "urea"],
        "sodium": ["sodium", "na", "serum sodium"],
        "potassium": ["potassium", "k", "serum potassium"],
    }
    
    COMMON_UNITS = {
        "g/dl": "g/dL",
        "g/100ml": "g/dL",
        "mg/dl": "mg/dL",
        "mg/100ml": "mg/dL",
        "meq/l": "mEq/L",
        "mmol/l": "mmol/L",
    }
    
    def __init__(self):
        """Initialize parameter extractor"""
        self.reverse_aliases = {}
        for param, aliases in self.PARAMETER_ALIASES.items():
            for alias in aliases:
                self.reverse_aliases[alias.lower()] = param
    
    def normalize_parameter_name(self, name: str) -> Optional[str]:
        normalized = name.lower().strip()
        
        # Direct match in reverse aliases
        if normalized in self.reverse_aliases:
            return self.reverse_aliases[normalized]
        
        # Fuzzy match if no direct match
        best_match = None
        best_score = 0.7  # Minimum similarity threshold
        
        for alias, param in self.reverse_aliases.items():
            score = SequenceMatcher(None, normalized, alias).ratio()
            if score > best_score:
                best_score = score
                best_match = param
        
        return best_match
    
    def normalize_unit(self, unit: str) -> str:
        normalized = unit.lower().strip()
        return self.COMMON_UNITS.get(normalized, unit)
    
    def extract_parameters(self, text: str) -> List[Dict[str, Any]]:
        parameters = []
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip() or len(line.strip()) < 3:
                continue
            
            pattern = r'([a-zA-Z\s\-/]+?)[\s:]+(\d+\.?\d*)\s*([a-zA-Z\/%]+)'
            matches = re.finditer(pattern, line)
            
            for match in matches:
                param_name = match.group(1).strip()
                value_str = match.group(2).strip()
                unit = match.group(3).strip()
                
                normalized_param = self.normalize_parameter_name(param_name)
                
                if normalized_param:
                    try:
                        value = float(value_str)
                        normalized_unit = self.normalize_unit(unit)
                        
                        parameters.append({
                            "parameter": normalized_param,
                            "raw_name": param_name,
                            "value": value,
                            "unit": normalized_unit,
                            "source_line": line.strip()
                        })
                    except ValueError:
                        logger.warning(f"Could not convert value to float: {value_str}")
        
        return parameters


class DataExtractionEngine:
    """Main engine for data extraction"""
    
    def __init__(self):
        self.parameter_extractor = ParameterExtractor()
        self.logger = logging.getLogger(__name__)
    
    def extract(self, parsed_report: Dict[str, Any]) -> Dict[str, Any]:
        if not parsed_report.get("success"):
            return {
                "success": False,
                "error": parsed_report.get("error", "Parsing failed"),
                "parameters": []
            }
        
        content = parsed_report.get("content", "")
        
        if parsed_report.get("format") == "json":
            return self._extract_from_json(content)
        
        extracted_params = self.parameter_extractor.extract_parameters(content)
        
        return {
            "success": True,
            "format": parsed_report.get("format"),
            "file_path": parsed_report.get("file_path"),
            "parameters": extracted_params,
            "total_parameters_found": len(extracted_params),
            "metadata": parsed_report.get("metadata", {})
        }
    
    def _extract_from_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        parameters = []
        
        if "parameters" in json_data and isinstance(json_data["parameters"], dict):
            params_section = json_data["parameters"]
            for key, value_obj in params_section.items():
                if isinstance(value_obj, dict) and "value" in value_obj:
                    value = value_obj.get("value")
                    unit = value_obj.get("unit", "")
                    normalized_param = self.parameter_extractor.normalize_parameter_name(key)
                    if normalized_param and isinstance(value, (int, float)):
                        parameters.append({
                            "parameter": normalized_param,
                            "raw_name": key,
                            "value": float(value),
                            "unit": unit,
                            "source": json_data
                        })
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key != "parameters" and isinstance(value, (int, float)):
                    normalized_param = self.parameter_extractor.normalize_parameter_name(key)
                    if normalized_param:
                        parameters.append({
                            "parameter": normalized_param,
                            "raw_name": key,
                            "value": float(value),
                            "unit": "unit_not_specified",
                            "source": json_data
                        })
        
        return {
            "success": True,
            "format": "json",
            "parameters": parameters,
            "total_parameters_found": len(parameters)
        }
