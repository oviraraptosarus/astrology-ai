import sys, os

scanner_path = "E:/ASTROLOGY AI/forward_timing_scanner.py"
with open(scanner_path, "r", encoding="utf-8") as f:
    code = f.read()

old_transit_func = """        common_houses = list(set(jup_aspected_houses).intersection(set(sat_aspected_houses)))
        activated_target_houses = [h for h in common_houses if h in target_houses]
        jup_sav = self.sav_table.get(ZODIAC_SIGNS[jup_sign_idx], 28)

        reasons = []
        double_transit_active = len(activated_target_houses) > 0
        if double_transit_active:
            reasons.append(f"K.N. Rao Double Transit of Jupiter (H{jup_house}) & Saturn (H{sat_house}) jointly activates houses {activated_target_houses}")
        if jup_sav >= 28:
            reasons.append(f"Transit occurs in strong Ashtakavarga sign {ZODIAC_SIGNS[jup_sign_idx]} ({jup_sav} bindus)")

        transit_score = min(35, (len(activated_target_houses) * 12) + (5 if jup_sav >= 28 else 0))

        return {
            "double_transit_active": double_transit_active,
            "activated_houses": activated_target_houses,
            "transit_score": transit_score,
            "kakshya_favorable": jup_sav >= 28,
            "reasons": reasons
        }"""

new_transit_func = """        # Classical K.N. Rao Double Transit Evaluation
        # 1. Exact Single-House Convergence (both aspecting the exact same target house)
        exact_common = list(set(jup_aspected_houses).intersection(set(sat_aspected_houses)))
        exact_target = [h for h in exact_common if h in target_houses]

        # 2. Domain-Level Activation (Jupiter touching one domain house/lord AND Saturn touching one domain house/lord)
        jup_domain_hits = [h for h in jup_aspected_houses if h in target_houses]
        sat_domain_hits = [h for h in sat_aspected_houses if h in target_houses]
        domain_double_active = (len(jup_domain_hits) > 0 and len(sat_domain_hits) > 0)

        jup_sav = self.sav_table.get(ZODIAC_SIGNS[jup_sign_idx], 28)
        reasons = []
        
        double_transit_active = (len(exact_target) > 0) or domain_double_active
        activated_target_houses = list(set(exact_target + jup_domain_hits + sat_domain_hits))

        if len(exact_target) > 0:
            reasons.append(f"Exact K.N. Rao Double Transit: Jupiter (H{jup_house}) & Saturn (H{sat_house}) jointly aspect House(s) {exact_target}")
        elif domain_double_active:
            reasons.append(f"Domain Double Transit: Jupiter activates H{jup_domain_hits} while Saturn activates H{sat_domain_hits}")

        if jup_sav >= 28:
            reasons.append(f"Transit occurs in strong Ashtakavarga sign {ZODIAC_SIGNS[jup_sign_idx]} ({jup_sav} bindus)")

        # Scoring
        base_pts = 20 if len(exact_target) > 0 else (15 if domain_double_active else 0)
        house_pts = min(10, len(activated_target_houses) * 4)
        sav_pts = 5 if jup_sav >= 28 else 0
        transit_score = base_pts + house_pts + sav_pts

        return {
            "double_transit_active": double_transit_active,
            "activated_houses": activated_target_houses,
            "transit_score": min(35, transit_score),
            "kakshya_favorable": jup_sav >= 28,
            "reasons": reasons
        }"""

code = code.replace(old_transit_func, new_transit_func)
with open(scanner_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Double transit rule patched.")
