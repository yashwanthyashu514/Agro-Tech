# Module 4 – Crop Growth Stages (heat-unit / growing-degree-day model, no training needed)
crop_growth_stages.csv      : 27 crops x 6 stages (germination -> harvest), days after sowing, Kc, water need
crop_growth_master.csv      : crop duration, sowing date, base temperature, FAO-56 Kc values
perennial_crop_calendar.csv : 8 tree crops – flowering / harvest months
python predict_growth_stages.py --crop maize --sow 2026-06-20 --weather <weather csv for one location>
(make a one-location file with fetch_weather_nasa_power.py, or let agro_engine.py do it automatically)
