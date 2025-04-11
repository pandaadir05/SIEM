#!/usr/bin/env python3
import os
import yaml

def load_sigma_rules(rules_dir):
    sigma_rules = []
    if not os.path.isdir(rules_dir):
        print(f"[SigmaLoader] '{rules_dir}' not a directory.")
        return sigma_rules

    for fn in os.listdir(rules_dir):
        if fn.endswith(".yml") or fn.endswith(".yaml"):
            path = os.path.join(rules_dir, fn)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    rule_data = yaml.safe_load(f)
                    if rule_data:
                        sigma_rules.append(rule_data)
                        print(f"[SigmaLoader] Loaded rule: {rule_data.get('title')}")
                except yaml.YAMLError as e:
                    print(f"[SigmaLoader] Error in {fn}: {e}")
    print(f"[SigmaLoader] Total rules: {len(sigma_rules)}")
    return sigma_rules
