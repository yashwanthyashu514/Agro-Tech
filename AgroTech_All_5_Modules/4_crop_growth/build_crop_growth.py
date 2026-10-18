"""
Builds crop_growth_stages.csv, crop_growth_master.csv and perennial_crop_calendar.csv.

Stage day ranges = days after sowing (DAS) for a typical medium-duration variety grown
in Karnataka / peninsular India. They are TYPICAL values compiled from FAO-56 stage-length
guidance and standard Indian agronomy practice. Variety and sowing date change them by
+/- 10-20%, so check against the UAS Dharwad / UAS Bengaluru "Package of Practices" for
the varieties you model. predict_growth_stages.py adjusts them for temperature.

Kc (crop coefficient) values: FAO Irrigation & Drainage Paper 56, Table 12
(Kc_ini for crops without their own value = FAO-56 crop-group value).
"""
import pandas as pd

S = ["Germination / emergence", "Vegetative growth", "Flowering", "Grain / fruit formation", "Maturity"]

# crop: (category, season, typical_sowing (MM-DD), base_temp_C, kc_ini, kc_mid, kc_end, stage_ends[5],
#        stage names override or None, critical_irrigation_stages (indices), harvest_window_days)
CROPS = {
    "rice":        ("Cereal", "Kharif", "07-01", 10, 1.05, 1.20, 0.75, [7, 60, 90, 115, 125], None, [2, 3], 10),
    "maize":       ("Cereal", "Kharif", "06-15", 10, 0.30, 1.20, 0.50, [7, 50, 65, 95, 110], None, [2, 3], 10),
    "sorghum":     ("Cereal", "Kharif", "06-15", 10, 0.30, 1.05, 0.55, [7, 45, 70, 95, 110], None, [1, 2], 10),
    "finger millet": ("Cereal", "Kharif", "07-15", 10, 0.30, 1.00, 0.30, [8, 55, 75, 100, 115], None, [2, 3], 10),
    "pearl millet": ("Cereal", "Kharif", "06-20", 10, 0.30, 1.00, 0.30, [5, 35, 50, 70, 85], None, [2], 7),
    "wheat":       ("Cereal", "Rabi", "11-15", 5, 0.30, 1.15, 0.30, [7, 55, 75, 100, 110], None, [1, 2, 3], 10),
    "chickpea":    ("Pulse", "Rabi", "10-20", 5, 0.40, 1.00, 0.35, [10, 45, 65, 90, 100], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 7),
    "pigeonpeas":  ("Pulse", "Kharif", "06-20", 10, 0.40, 1.00, 0.35, [10, 90, 120, 145, 160], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 10),
    "mungbean":    ("Pulse", "Kharif", "06-15", 10, 0.40, 1.05, 0.35, [5, 30, 40, 55, 65], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 5),
    "blackgram":   ("Pulse", "Kharif", "06-15", 10, 0.40, 1.05, 0.35, [6, 35, 45, 65, 75], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 5),
    "mothbeans":   ("Pulse", "Kharif", "07-01", 10, 0.40, 1.00, 0.35, [6, 35, 45, 65, 75], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2], 5),
    "lentil":      ("Pulse", "Rabi", "11-01", 5, 0.40, 1.10, 0.30, [10, 50, 70, 95, 110], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 7),
    "kidneybeans": ("Pulse", "Rabi", "10-15", 10, 0.40, 1.15, 0.35, [8, 40, 55, 85, 100], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 7),
    "groundnut":   ("Oilseed", "Kharif", "06-20", 10, 0.40, 1.15, 0.60, [10, 30, 50, 90, 110], ["Germination / emergence", "Vegetative growth", "Flowering / pegging", "Pod formation / filling", "Maturity"], [2, 3], 7),
    "soybean":     ("Oilseed", "Kharif", "06-20", 10, 0.40, 1.15, 0.50, [7, 40, 55, 85, 100], ["Germination / emergence", "Vegetative growth", "Flowering", "Pod formation / seed filling", "Maturity"], [2, 3], 7),
    "sunflower":   ("Oilseed", "Kharif", "07-01", 7, 0.35, 1.05, 0.35, [8, 40, 60, 80, 95], ["Germination / emergence", "Vegetative growth", "Bud / flowering", "Seed filling", "Maturity"], [2, 3], 7),
    "cotton":      ("Fibre", "Kharif", "06-01", 15, 0.35, 1.15, 0.60, [10, 50, 90, 140, 170], ["Germination / emergence", "Vegetative growth", "Squaring / flowering", "Boll development", "Boll opening / maturity"], [2, 3], 30),
    "jute":        ("Fibre", "Kharif", "04-01", 10, 0.35, 1.15, 0.60, [7, 90, 105, 115, 120], ["Germination / emergence", "Vegetative growth", "Flowering", "Small-pod stage (fibre harvest)", "Maturity"], [1], 7),
    "sugarcane":   ("Cash crop", "Annual", "01-15", 12, 0.40, 1.25, 0.75, [35, 120, 270, 330, 365], ["Germination / sprouting", "Tillering", "Grand growth", "Ripening", "Maturity"], [1, 2], 30),
    "potato":      ("Vegetable", "Kharif", "06-15", 7, 0.50, 1.15, 0.75, [15, 35, 50, 85, 100], ["Sprouting / emergence", "Vegetative growth", "Tuber initiation (flowering)", "Tuber bulking", "Maturity"], [2, 3], 7),
    "onion":       ("Vegetable", "Kharif", "06-15", 6, 0.70, 1.05, 0.75, [10, 75, 90, 125, 140], ["Germination (nursery)", "Vegetative growth (incl. transplanting)", "Bulb initiation", "Bulb development", "Maturity"], [2, 3], 10),
    "tomato":      ("Vegetable", "Kharif", "06-01", 10, 0.60, 1.15, 0.80, [8, 55, 75, 110, 140], ["Germination (nursery)", "Vegetative growth (incl. transplanting)", "Flowering", "Fruit set / development", "Maturity / harvests"], [2, 3], 30),
    "chilli":      ("Vegetable", "Kharif", "07-01", 10, 0.60, 1.05, 0.90, [10, 70, 100, 150, 180], ["Germination (nursery)", "Vegetative growth (incl. transplanting)", "Flowering", "Fruit development", "Maturity / harvests"], [2, 3], 30),
    "watermelon":  ("Fruit (annual)", "Zaid", "01-01", 10, 0.40, 1.00, 0.75, [7, 30, 45, 75, 90], ["Germination / emergence", "Vine growth", "Flowering", "Fruit development", "Maturity"], [2, 3], 10),
    "muskmelon":   ("Fruit (annual)", "Zaid", "01-15", 10, 0.50, 0.85, 0.60, [7, 30, 42, 72, 85], ["Germination / emergence", "Vine growth", "Flowering", "Fruit development", "Maturity"], [2, 3], 10),
    "banana":      ("Fruit", "Annual", "06-01", 14, 0.50, 1.10, 1.00, [60, 180, 240, 330, 365], ["Establishment (from sucker)", "Vegetative growth", "Shooting / flowering", "Bunch development", "Maturity"], [2, 3], 20),
    "papaya":      ("Fruit", "Annual", "06-01", 15, 0.60, 1.00, 0.90, [30, 120, 180, 270, 300], ["Establishment (after transplanting)", "Vegetative growth", "Flowering", "Fruit development", "First harvest (then continuous)"], [2, 3], 60),
}

# High / Medium / Low water need per stage, derived from where the stage sits on the FAO Kc curve
WATER = ["Low", "Medium", "High", "High", "Low"]


def build():
    stages, master = [], []
    for crop, (cat, season, sow, tb, ki, km, ke, ends, names, crit, hw) in CROPS.items():
        names = names or S
        start = 0
        for i, (nm, end) in enumerate(zip(names, ends)):
            kc = ki if i == 0 else (round((ki + km) / 2, 2) if i == 1 else (km if i in (2, 3) else ke))
            stages.append(dict(crop=crop, stage_no=i + 1, growth_stage=nm, start_day=start, end_day=end,
                               duration_days=end - start + 1, kc=kc, water_need=WATER[i],
                               critical_irrigation=("Yes" if i in crit else "No")))
            start = end + 1
        stages.append(dict(crop=crop, stage_no=6, growth_stage="Harvest", start_day=ends[-1],
                           end_day=ends[-1] + hw, duration_days=hw, kc=ke, water_need="Stop irrigation",
                           critical_irrigation="No"))
        master.append(dict(crop=crop, category=cat, main_season_karnataka=season, typical_sowing_date=sow,
                           total_duration_days=ends[-1], base_temp_c=tb, kc_ini=ki, kc_mid=km, kc_end=ke))
    pd.DataFrame(stages).to_csv("crop_growth_stages.csv", index=False)
    pd.DataFrame(master).to_csv("crop_growth_master.csv", index=False)

    # Perennial tree crops: yearly cycle by month, not days after sowing
    per = [
        ("mango", "4-5 (grafted)", "Dec-Feb", "Feb-Mar", "Mar-May", "Apr-Jun",
         "Flowering after dry, cool spell; avoid irrigation before flowering"),
        ("coconut", "5-6 (tall), 3-4 (dwarf)", "Year-round", "Year-round", "~12 months spathe to mature nut",
         "Year-round, every 45-60 days", "Continuous bearing"),
        ("coffee", "3-4", "Feb-Apr (after blossom showers)", "Mar-May", "Apr-Nov (arabica ~8 months, robusta ~10 months)",
         "Nov-Feb (arabica), Dec-Mar (robusta)", "Blossom & backing showers / irrigation are critical"),
        ("grapes", "2", "~30-40 days after Oct fruit pruning", "Nov", "Nov-Feb",
         "Jan-Apr (110-150 days after fruit pruning)", "Two prunings per year: Apr (foundation), Oct (fruit)"),
        ("pomegranate", "2-3", "Jun-Jul (mrig bahar) / Sep-Oct (hasta) / Jan-Feb (ambe)", "1 month after flowering",
         "4-5 months", "Nov-Jan (mrig) / Feb-Apr (hasta) / Jun-Aug (ambe)",
         "Flowering season chosen by withholding water ('bahar' treatment)"),
        ("orange", "4-5 (mandarin)", "Jan-Mar", "Mar-Apr", "Apr-Nov", "Nov-Feb", "Coorg mandarin calendar"),
        ("apple", "4-5", "Mar-Apr", "Apr-May", "May-Aug", "Jul-Oct", "Temperate (Himalayan states); not grown in Karnataka"),
        ("arecanut", "5-6", "Year-round (peak Jan-Mar)", "Feb-Apr", "8-10 months", "Oct-Feb", "Major Karnataka plantation crop"),
    ]
    pd.DataFrame(per, columns=["crop", "years_to_first_bearing", "flowering", "fruit_set", "fruit_development",
                               "harvest", "notes"]).to_csv("perennial_crop_calendar.csv", index=False)
    print(len(stages), "stage rows for", len(CROPS), "crops;", len(per), "perennial crops")


if __name__ == "__main__":
    build()
