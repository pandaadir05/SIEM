#!/usr/bin/env python3
import re

SIGMA_OPERATORS = {
    "|equals": lambda field_val, rule_val: field_val == rule_val,
    "|contains": lambda field_val, rule_val: rule_val in field_val,
    "|startswith": lambda field_val, rule_val: field_val.startswith(rule_val),
    "|endswith": lambda field_val, rule_val: field_val.endswith(rule_val),
    "|regex": lambda field_val, rule_val: bool(re.search(rule_val, field_val))
}

def advanced_sigma_to_python_condition(rule):
    detection = rule.get("detection", {})
    condition = detection.get("condition", "").strip().lower()
    selection = detection.get("selection", {})

    if condition != "selection" or not selection:
        return None

    checks = []

    for key, val in selection.items():
        found_operator = False
        for op, func in SIGMA_OPERATORS.items():
            if op in key:
                field_name = key.replace(op, "").strip()
                expected_val = str(val).lower()
                def rule_check(event, f=field_name, ev=expected_val, opf=func):
                    fv = str(event.get(f,"")).lower()
                    return opf(fv, ev)
                checks.append(rule_check)
                found_operator = True
                break
        if not found_operator:
            pass

    if not checks:
        return None

    def combined_check(event):
        return all(chk(event) for chk in checks)

    return combined_check
