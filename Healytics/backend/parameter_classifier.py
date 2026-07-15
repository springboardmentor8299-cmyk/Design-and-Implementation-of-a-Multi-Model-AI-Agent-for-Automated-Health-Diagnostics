# backend/parameter_classifier.py
"""
Parameter Classification Engine (Model 1)
Compares each blood parameter against standard/gender-specific reference ranges.
Returns: Normal | High | Low | Critical High | Critical Low
"""

from backend.reference_ranges import REFERENCE_RANGES, CRITICAL_THRESHOLDS


class ParameterClassifier:

    STATUS_NORMAL        = "Normal"
    STATUS_HIGH          = "High"
    STATUS_LOW           = "Low"
    STATUS_CRITICAL_HIGH = "Critical High"
    STATUS_CRITICAL_LOW  = "Critical Low"
    STATUS_UNKNOWN       = "Unknown"

    def classify_all(self, parameters: dict, gender: str = "general") -> list:
        """
        Classify all parameters in the dict.
        Returns a list of classification result dicts, sorted by category.
        """
        results = []
        for param_key, value in parameters.items():
            if value is None:
                continue
            result = self.classify_one(param_key, float(value), gender)
            if result:
                results.append(result)

        # Sort by category then display name
        results.sort(key=lambda x: (x["category"], x["display_name"]))
        return results

    def classify_one(self, param_key: str, value: float, gender: str = "general") -> dict:
        """
        Classify a single parameter.
        Returns a rich dict with status, reference range, severity, etc.
        """
        ref = REFERENCE_RANGES.get(param_key)
        if not ref:
            return None

        # Pick gender-specific range, fall back to general
        gender = gender.lower() if gender else "general"
        range_data = ref.get(gender) or ref.get("general") or {}

        min_val = range_data.get("min", 0)
        max_val = range_data.get("max", float("inf"))
        unit    = range_data.get("unit", "")

        # Determine status
        status   = self.STATUS_NORMAL
        severity = "normal"

        # Check critical thresholds first
        critical = CRITICAL_THRESHOLDS.get(param_key, {})
        crit_low  = critical.get("critical_low")
        crit_high = critical.get("critical_high")

        if crit_low is not None and value < crit_low:
            status   = self.STATUS_CRITICAL_LOW
            severity = "critical"
        elif crit_high is not None and value > crit_high:
            status   = self.STATUS_CRITICAL_HIGH
            severity = "critical"
        elif value < min_val:
            status   = self.STATUS_LOW
            severity = "warning"
        elif max_val != float("inf") and value > max_val:
            status   = self.STATUS_HIGH
            severity = "warning"
        else:
            status   = self.STATUS_NORMAL
            severity = "normal"

        # Percentage deviation from midpoint (for health score contribution)
        if max_val != float("inf") and min_val is not None:
            midpoint = (min_val + max_val) / 2
            deviation_pct = abs(value - midpoint) / max(midpoint, 0.001) * 100
        else:
            deviation_pct = 0.0

        # Reference range string
        if max_val == float("inf") or max_val == 999:
            ref_range_str = f"> {min_val} {unit}"
        elif min_val == 0:
            ref_range_str = f"< {max_val} {unit}"
        else:
            ref_range_str = f"{min_val} – {max_val} {unit}"

        return {
            "param_key":      param_key,
            "display_name":   ref.get("display_name", param_key),
            "category":       ref.get("category", "Other"),
            "value":          value,
            "unit":           unit,
            "status":         status,
            "severity":       severity,       # "normal" | "warning" | "critical"
            "min_ref":        min_val,
            "max_ref":        max_val,
            "ref_range_str":  ref_range_str,
            "deviation_pct":  round(deviation_pct, 1),
        }

    def get_summary_counts(self, classified: list) -> dict:
        """
        Returns counts: total, normal, high, low, critical.
        """
        counts = {
            "total":    len(classified),
            "normal":   0,
            "high":     0,
            "low":      0,
            "critical": 0,
            "elevated": 0,   # high + critical high
            "below":    0,   # low + critical low
        }
        for item in classified:
            s = item["status"]
            if s == self.STATUS_NORMAL:
                counts["normal"] += 1
            elif s in (self.STATUS_HIGH, self.STATUS_CRITICAL_HIGH):
                counts["high"] += 1
                counts["elevated"] += 1
            elif s in (self.STATUS_LOW, self.STATUS_CRITICAL_LOW):
                counts["low"] += 1
                counts["below"] += 1
            if item["severity"] == "critical":
                counts["critical"] += 1
        return counts

    def get_abnormal(self, classified: list) -> list:
        """Returns only the abnormal parameters."""
        return [c for c in classified if c["status"] != self.STATUS_NORMAL]

    def get_critical(self, classified: list) -> list:
        """Returns only the critical parameters."""
        return [c for c in classified if c["severity"] == "critical"]