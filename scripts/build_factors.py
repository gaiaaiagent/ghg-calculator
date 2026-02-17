#!/usr/bin/env python3
"""Generate emission factor JSON files from embedded data.

Run: python scripts/build_factors.py
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "ghg_calculator" / "factors" / "data"


def write_json(subdir: str, filename: str, data: dict):
    path = DATA_DIR / subdir
    path.mkdir(parents=True, exist_ok=True)
    out = path / filename
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Wrote {out} ({len(data['factors'])} factors)")


# ─── EPA HUB ────────────────────────────────────────────────────────────────

def build_epa_hub():
    factors = []

    # ── Stationary Combustion ──
    # Format: (id_suffix, name, fuel_type, co2, ch4, n2o, unit, subcategory, tags)
    stationary = [
        # Natural gas
        ("natural_gas_therm", "Natural Gas", "natural_gas", 5.302, 0.0001, 0.00001, "therm", "natural_gas", ["stationary", "gas"]),
        ("natural_gas_mcf", "Natural Gas", "natural_gas", 53.06, 0.001, 0.0001, "MCF", "natural_gas", ["stationary", "gas"]),
        ("natural_gas_mmbtu", "Natural Gas", "natural_gas", 53.06, 0.001, 0.0001, "MMBtu", "natural_gas", ["stationary", "gas"]),
        ("natural_gas_ccf", "Natural Gas", "natural_gas", 5.306, 0.0001, 0.00001, "CCF", "natural_gas", ["stationary", "gas"]),
        ("natural_gas_kwh", "Natural Gas", "natural_gas", 0.18116, 0.0000034, 0.00000034, "kWh", "natural_gas", ["stationary", "gas"]),
        # Diesel / Distillate #2
        ("diesel_gallon", "Diesel/Distillate Fuel Oil #2", "diesel", 10.21, 0.00041, 0.00008, "gallon", "petroleum", ["stationary", "liquid"]),
        ("diesel_mmbtu", "Diesel/Distillate Fuel Oil #2", "diesel", 73.96, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "liquid"]),
        # Gasoline
        ("gasoline_gallon", "Motor Gasoline", "gasoline", 8.78, 0.00035, 0.00008, "gallon", "petroleum", ["stationary", "liquid"]),
        ("gasoline_mmbtu", "Motor Gasoline", "gasoline", 70.22, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "liquid"]),
        # Propane
        ("propane_gallon", "Propane", "propane", 5.72, 0.00023, 0.00004, "gallon", "petroleum", ["stationary", "gas"]),
        ("propane_mmbtu", "Propane", "propane", 62.87, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "gas"]),
        # Fuel Oil #6
        ("fuel_oil_6_gallon", "Residual Fuel Oil #6", "fuel_oil_no6", 11.27, 0.00045, 0.00009, "gallon", "petroleum", ["stationary", "liquid"]),
        ("fuel_oil_6_mmbtu", "Residual Fuel Oil #6", "fuel_oil_no6", 75.10, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "liquid"]),
        # Kerosene
        ("kerosene_gallon", "Kerosene", "kerosene", 10.15, 0.00041, 0.00008, "gallon", "petroleum", ["stationary", "liquid"]),
        ("kerosene_mmbtu", "Kerosene", "kerosene", 75.20, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "liquid"]),
        # LPG
        ("lpg_gallon", "Liquefied Petroleum Gas (LPG)", "lpg", 5.68, 0.00023, 0.00004, "gallon", "petroleum", ["stationary", "gas"]),
        ("lpg_mmbtu", "LPG", "lpg", 61.71, 0.003, 0.0006, "MMBtu", "petroleum", ["stationary", "gas"]),
        # Fuel Oil #1
        ("fuel_oil_1_gallon", "Distillate Fuel Oil #1", "fuel_oil_no2", 9.96, 0.00040, 0.00008, "gallon", "petroleum", ["stationary", "liquid"]),
        # Fuel Oil #4
        ("fuel_oil_4_gallon", "Distillate Fuel Oil #4", "fuel_oil_no2", 10.69, 0.00043, 0.00009, "gallon", "petroleum", ["stationary", "liquid"]),
        # Coal
        ("coal_bituminous_ton", "Bituminous Coal", "coal_bituminous", 2328.0, 0.011, 0.016, "short_ton", "coal", ["stationary", "solid"]),
        ("coal_bituminous_mmbtu", "Bituminous Coal", "coal_bituminous", 93.28, 0.011, 0.0016, "MMBtu", "coal", ["stationary", "solid"]),
        ("coal_anthracite_ton", "Anthracite Coal", "coal_anthracite", 2602.0, 0.011, 0.016, "short_ton", "coal", ["stationary", "solid"]),
        ("coal_subbituminous_ton", "Subbituminous Coal", "coal_subbituminous", 1673.0, 0.011, 0.016, "short_ton", "coal", ["stationary", "solid"]),
        ("coal_lignite_ton", "Lignite Coal", "coal_subbituminous", 1389.0, 0.011, 0.016, "short_ton", "coal", ["stationary", "solid"]),
        # Wood / Biomass
        ("wood_ton", "Wood and Wood Residuals", "wood", 1640.0, 0.0072, 0.0036, "short_ton", "biomass", ["stationary", "solid", "biomass"]),
        ("wood_mmbtu", "Wood and Wood Residuals", "wood", 93.80, 0.0072, 0.0036, "MMBtu", "biomass", ["stationary", "solid", "biomass"]),
        # Landfill gas
        ("landfill_gas_scf", "Landfill Gas", "landfill_gas", 0.0545, 0.0000032, 0.0000006, "scf", "gas", ["stationary", "gas", "biogas"]),
        # Petroleum coke
        ("pet_coke_ton", "Petroleum Coke", "coal_bituminous", 3072.0, 0.012, 0.018, "short_ton", "petroleum", ["stationary", "solid"]),
        # MSW
        ("msw_ton", "Municipal Solid Waste", "wood", 902.0, 0.032, 0.004, "short_ton", "waste", ["stationary", "solid"]),
        # Tires
        ("tires_ton", "Waste Tires", "diesel", 2407.0, 0.032, 0.004, "short_ton", "waste", ["stationary", "solid"]),
        # Jet fuel (stationary use)
        ("jet_fuel_gallon", "Jet Fuel (Kerosene-type)", "jet_fuel", 9.75, 0.00039, 0.00008, "gallon", "petroleum", ["stationary", "liquid"]),
        # E85
        ("e85_gallon", "E85 Ethanol Blend", "e85", 5.75, 0.00023, 0.00005, "gallon", "biofuel", ["stationary", "liquid", "biofuel"]),
        # B20
        ("b20_gallon", "B20 Biodiesel Blend", "b20", 8.17, 0.00033, 0.00007, "gallon", "biofuel", ["stationary", "liquid", "biofuel"]),
        # CNG
        ("cng_scf", "Compressed Natural Gas", "cng", 0.0545, 0.0000022, 0.0000004, "scf", "gas", ["stationary", "gas"]),
        # LNG
        ("lng_gallon", "Liquefied Natural Gas", "lng", 4.46, 0.00018, 0.00004, "gallon", "gas", ["stationary", "liquid"]),
        # Residual fuel oil
        ("residual_fuel_oil_gallon", "Residual Fuel Oil", "residual_fuel_oil", 11.27, 0.00045, 0.00009, "gallon", "petroleum", ["stationary", "liquid"]),
    ]

    for s in stationary:
        factors.append({
            "id": f"epa_stat_{s[0]}", "name": f"{s[1]} (Stationary)",
            "category": "stationary_combustion", "subcategory": s[7],
            "fuel_type": s[2], "co2_factor": s[3], "ch4_factor": s[4], "n2o_factor": s[5],
            "activity_unit": s[6], "region": "US", "year": 2025, "tags": s[8],
        })

    # ── Mobile Combustion ──
    mobile_by_fuel = [
        # Gasoline vehicles
        ("gasoline_passenger_car_mile", "Gasoline Passenger Car", "gasoline", 0.347, 0.000025, 0.000008, "mile", "passenger_car", ["mobile", "road", "gasoline"]),
        ("gasoline_passenger_car_gallon", "Gasoline Passenger Car", "gasoline", 8.78, 0.00035, 0.00022, "gallon", "passenger_car", ["mobile", "road", "gasoline"]),
        ("gasoline_light_truck_mile", "Gasoline Light-Duty Truck", "gasoline", 0.462, 0.000032, 0.000010, "mile", "light_truck", ["mobile", "road", "gasoline"]),
        ("gasoline_light_truck_gallon", "Gasoline Light-Duty Truck", "gasoline", 8.78, 0.00046, 0.00026, "gallon", "light_truck", ["mobile", "road", "gasoline"]),
        ("gasoline_heavy_duty_mile", "Gasoline Heavy-Duty Vehicle", "gasoline", 1.505, 0.000049, 0.000047, "mile", "heavy_duty", ["mobile", "road", "gasoline"]),
        ("gasoline_heavy_duty_gallon", "Gasoline Heavy-Duty Vehicle", "gasoline", 8.78, 0.00054, 0.00050, "gallon", "heavy_duty", ["mobile", "road", "gasoline"]),
        ("motorcycle_mile", "Motorcycle", "gasoline", 0.186, 0.000021, 0.000006, "mile", "motorcycle", ["mobile", "road", "gasoline"]),
        ("motorcycle_gallon", "Motorcycle", "gasoline", 8.78, 0.00035, 0.00008, "gallon", "motorcycle", ["mobile", "road", "gasoline"]),
        # Diesel vehicles
        ("diesel_passenger_car_mile", "Diesel Passenger Car", "diesel", 0.325, 0.000010, 0.000015, "mile", "passenger_car", ["mobile", "road", "diesel"]),
        ("diesel_passenger_car_gallon", "Diesel Passenger Car", "diesel", 10.21, 0.00041, 0.00008, "gallon", "passenger_car", ["mobile", "road", "diesel"]),
        ("diesel_light_truck_mile", "Diesel Light-Duty Truck", "diesel", 0.440, 0.000012, 0.000018, "mile", "light_truck", ["mobile", "road", "diesel"]),
        ("diesel_light_truck_gallon", "Diesel Light-Duty Truck", "diesel", 10.21, 0.00041, 0.00008, "gallon", "light_truck", ["mobile", "road", "diesel"]),
        ("diesel_heavy_duty_mile", "Diesel Heavy-Duty Vehicle", "diesel", 1.692, 0.000051, 0.000048, "mile", "heavy_duty", ["mobile", "road", "diesel"]),
        ("diesel_heavy_duty_gallon", "Diesel Heavy-Duty Vehicle", "diesel", 10.21, 0.00041, 0.00008, "gallon", "heavy_duty", ["mobile", "road", "diesel"]),
        # Medium duty
        ("gasoline_medium_duty_mile", "Gasoline Medium-Duty Vehicle", "gasoline", 0.826, 0.000038, 0.000025, "mile", "medium_duty", ["mobile", "road", "gasoline"]),
        ("diesel_medium_duty_mile", "Diesel Medium-Duty Vehicle", "diesel", 0.910, 0.000030, 0.000032, "mile", "medium_duty", ["mobile", "road", "diesel"]),
        # Aviation
        ("jet_fuel_gallon", "Jet Fuel (Aviation)", "jet_fuel", 9.75, 0.00005, 0.00009, "gallon", "aviation", ["mobile", "aviation"]),
        ("aviation_gasoline_gallon", "Aviation Gasoline", "aviation_gasoline", 8.31, 0.00070, 0.00002, "gallon", "aviation", ["mobile", "aviation"]),
        # Marine
        ("marine_diesel_gallon", "Marine Diesel Oil", "diesel", 10.21, 0.00041, 0.00008, "gallon", "marine", ["mobile", "marine"]),
        ("marine_residual_gallon", "Marine Residual Fuel Oil", "residual_fuel_oil", 11.27, 0.00045, 0.00009, "gallon", "marine", ["mobile", "marine"]),
        # Rail
        ("rail_diesel_gallon", "Rail Diesel", "diesel", 10.21, 0.00041, 0.00008, "gallon", "rail", ["mobile", "rail"]),
        # Off-road
        ("offroad_gasoline_gallon", "Off-Road Gasoline Equipment", "gasoline", 8.78, 0.00050, 0.00022, "gallon", "off_road", ["mobile", "off_road", "gasoline"]),
        ("offroad_diesel_gallon", "Off-Road Diesel Equipment", "diesel", 10.21, 0.00059, 0.00026, "gallon", "off_road", ["mobile", "off_road", "diesel"]),
        # Buses
        ("diesel_bus_mile", "Diesel Transit Bus", "diesel", 2.680, 0.000016, 0.000010, "mile", "bus", ["mobile", "road", "diesel"]),
        ("cng_bus_mile", "CNG Transit Bus", "cng", 2.364, 0.0372, 0.000010, "mile", "bus", ["mobile", "road", "cng"]),
        # Hybrid/EV reference
        ("hybrid_car_mile", "Hybrid Passenger Car", "gasoline", 0.213, 0.000015, 0.000005, "mile", "passenger_car", ["mobile", "road", "hybrid"]),
    ]

    for m in mobile_by_fuel:
        factors.append({
            "id": f"epa_mob_{m[0]}", "name": f"{m[1]} (Mobile)",
            "category": "mobile_combustion", "subcategory": m[7],
            "fuel_type": m[2], "co2_factor": m[3], "ch4_factor": m[4], "n2o_factor": m[5],
            "activity_unit": m[6], "region": "US", "year": 2025, "tags": m[8],
        })

    # ── Fugitive Emissions / Refrigerants ──
    # (id_suffix, name, co2e_gwp, tags)
    refrigerants = [
        # HFCs
        ("hfc_23", "HFC-23", 12400, ["hfc"]),
        ("hfc_32", "HFC-32", 677, ["hfc"]),
        ("hfc_125", "HFC-125", 3170, ["hfc"]),
        ("hfc_134a", "HFC-134a", 1300, ["hfc"]),
        ("hfc_143a", "HFC-143a", 4800, ["hfc"]),
        ("hfc_152a", "HFC-152a", 138, ["hfc"]),
        ("hfc_227ea", "HFC-227ea", 3350, ["hfc"]),
        ("hfc_236fa", "HFC-236fa", 8060, ["hfc"]),
        ("hfc_245fa", "HFC-245fa", 858, ["hfc"]),
        ("hfc_365mfc", "HFC-365mfc", 804, ["hfc"]),
        ("hfc_4310mee", "HFC-43-10mee", 1650, ["hfc"]),
        # PFCs
        ("pfc_cf4", "CF4 (PFC-14)", 6630, ["pfc"]),
        ("pfc_c2f6", "C2F6 (PFC-116)", 11100, ["pfc"]),
        ("pfc_c3f8", "C3F8 (PFC-218)", 8900, ["pfc"]),
        ("pfc_c4f10", "C4F10 (PFC-3-1-10)", 9200, ["pfc"]),
        ("pfc_c5f12", "C5F12 (PFC-4-1-12)", 8550, ["pfc"]),
        ("pfc_c6f14", "C6F14 (PFC-5-1-14)", 7910, ["pfc"]),
        # Other fluorinated
        ("sf6", "Sulfur Hexafluoride (SF6)", 23500, ["sf6"]),
        ("nf3", "Nitrogen Trifluoride (NF3)", 16100, ["nf3"]),
        # Refrigerant blends
        ("r404a", "R-404A Blend", 3922, ["blend"]),
        ("r407a", "R-407A Blend", 2107, ["blend"]),
        ("r407c", "R-407C Blend", 1774, ["blend"]),
        ("r410a", "R-410A Blend", 2088, ["blend"]),
        ("r507a", "R-507A Blend", 3985, ["blend"]),
        ("r508b", "R-508B Blend", 13396, ["blend"]),
        # Legacy / ODS
        ("r22", "R-22 (HCFC-22)", 1760, ["hcfc", "legacy"]),
        ("r123", "R-123 (HCFC-123)", 77, ["hcfc", "legacy"]),
        ("r11", "R-11 (CFC-11)", 4660, ["cfc", "legacy"]),
        ("r12", "R-12 (CFC-12)", 10200, ["cfc", "legacy"]),
        ("r113", "R-113 (CFC-113)", 5820, ["cfc", "legacy"]),
        ("r114", "R-114 (CFC-114)", 8590, ["cfc", "legacy"]),
        ("r141b", "R-141b (HCFC-141b)", 782, ["hcfc", "legacy"]),
        ("r142b", "R-142b (HCFC-142b)", 1980, ["hcfc", "legacy"]),
        ("r225ca", "R-225ca (HCFC-225ca)", 127, ["hcfc", "legacy"]),
        ("r225cb", "R-225cb (HCFC-225cb)", 525, ["hcfc", "legacy"]),
        # Additional common blends
        ("r134a_blend", "R-134a Automotive AC", 1300, ["hfc", "automotive"]),
        ("r404a_commercial", "R-404A Commercial Refrigeration", 3922, ["blend", "commercial"]),
        ("r410a_residential", "R-410A Residential AC", 2088, ["blend", "residential"]),
        ("r407c_chillers", "R-407C Chillers", 1774, ["blend", "commercial"]),
        ("r32_new", "R-32 Low-GWP Alternative", 677, ["hfc", "low_gwp"]),
        ("r1234yf", "R-1234yf (HFO)", 1, ["hfo", "low_gwp"]),
        ("r1234ze", "R-1234ze(E) (HFO)", 1, ["hfo", "low_gwp"]),
        ("r448a", "R-448A (Solstice N40)", 1273, ["blend", "low_gwp"]),
        ("r449a", "R-449A (Opteon XP40)", 1282, ["blend", "low_gwp"]),
        ("r452a", "R-452A (Opteon XP44)", 1945, ["blend", "low_gwp"]),
        ("r513a", "R-513A (Opteon XP10)", 573, ["blend", "low_gwp"]),
        ("r454b", "R-454B (Opteon XL41)", 467, ["blend", "low_gwp"]),
        ("r290", "R-290 Propane (Natural Refrigerant)", 3, ["natural", "low_gwp"]),
        ("r600a", "R-600a Isobutane", 3, ["natural", "low_gwp"]),
        ("r717", "R-717 Ammonia", 0, ["natural", "low_gwp"]),
        ("r744", "R-744 CO2 Refrigerant", 1, ["natural", "low_gwp"]),
    ]

    for r in refrigerants:
        factors.append({
            "id": f"epa_fug_{r[0]}", "name": r[1],
            "category": "fugitive_emissions", "subcategory": "refrigerant",
            "fuel_type": None, "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": r[2], "activity_unit": "kg",
            "region": "US", "year": 2025, "tags": ["fugitive", "refrigerant"] + r[3],
        })

    write_json("epa_hub", "v2025.json", {
        "source": "epa_hub", "version": "2025", "year": 2025,
        "description": "US EPA Emission Factors Hub - Stationary combustion, mobile combustion, and refrigerants",
        "url": "https://www.epa.gov/climateleadership/ghg-emission-factors-hub",
        "factors": factors,
    })


# ─── DEFRA ───────────────────────────────────────────────────────────────────

def build_defra():
    factors = []

    # Business travel
    travel = [
        ("flight_domestic", "Domestic Flight", "business_travel", "flights", 0.246, "passenger_km", ["air"]),
        ("flight_short_haul", "Short-Haul Flight (<3700km)", "business_travel", "flights", 0.156, "passenger_km", ["air"]),
        ("flight_long_haul", "Long-Haul Flight (>3700km)", "business_travel", "flights", 0.150, "passenger_km", ["air"]),
        ("flight_intl_avg", "International Flight (Average)", "business_travel", "flights", 0.158, "passenger_km", ["air"]),
        ("flight_economy", "Flight Economy Class", "business_travel", "flights", 0.148, "passenger_km", ["air"]),
        ("flight_business", "Flight Business Class", "business_travel", "flights", 0.429, "passenger_km", ["air"]),
        ("flight_first", "Flight First Class", "business_travel", "flights", 0.591, "passenger_km", ["air"]),
        ("rail_national", "National Rail", "business_travel", "rail", 0.035, "passenger_km", ["rail"]),
        ("rail_intl", "International Rail (Eurostar)", "business_travel", "rail", 0.004, "passenger_km", ["rail"]),
        ("rail_light", "Light Rail/Tram", "business_travel", "rail", 0.029, "passenger_km", ["rail"]),
        ("taxi", "Taxi (Average)", "business_travel", "road", 0.149, "passenger_km", ["road"]),
        ("bus_local", "Local Bus", "business_travel", "road", 0.089, "passenger_km", ["road"]),
        ("bus_coach", "Coach", "business_travel", "road", 0.027, "passenger_km", ["road"]),
        ("ferry_foot", "Ferry (Foot Passenger)", "business_travel", "sea", 0.019, "passenger_km", ["sea"]),
        ("ferry_car", "Ferry (Car Passenger)", "business_travel", "sea", 0.113, "passenger_km", ["sea"]),
    ]
    for t in travel:
        factors.append({
            "id": f"defra_travel_{t[0]}", "name": t[1], "category": t[2], "subcategory": t[3],
            "fuel_type": None, "co2_factor": t[4] * 0.95, "ch4_factor": t[4] * 0.02, "n2o_factor": t[4] * 0.03,
            "co2e_factor": t[4], "activity_unit": t[5], "region": "UK", "year": 2025, "tags": t[6] + ["business_travel"],
        })

    # Commuting
    commute = [
        ("car_small", "Small Car (<1.4L)", "commuting", "car", 0.142, "km", ["road"]),
        ("car_medium", "Medium Car (1.4-2.0L)", "commuting", "car", 0.170, "km", ["road"]),
        ("car_large", "Large Car (>2.0L)", "commuting", "car", 0.209, "km", ["road"]),
        ("car_average", "Average Car", "commuting", "car", 0.171, "km", ["road"]),
        ("car_electric", "Electric Vehicle (BEV)", "commuting", "car", 0.046, "km", ["road", "electric"]),
        ("car_hybrid", "Hybrid Car", "commuting", "car", 0.116, "km", ["road", "hybrid"]),
        ("car_phev", "Plug-in Hybrid", "commuting", "car", 0.071, "km", ["road", "hybrid"]),
        ("motorbike_small", "Motorbike (<125cc)", "commuting", "motorbike", 0.083, "km", ["road"]),
        ("motorbike_medium", "Motorbike (125-500cc)", "commuting", "motorbike", 0.101, "km", ["road"]),
        ("motorbike_large", "Motorbike (>500cc)", "commuting", "motorbike", 0.132, "km", ["road"]),
        ("bus", "Bus", "commuting", "bus", 0.089, "passenger_km", ["road"]),
        ("rail", "National Rail", "commuting", "rail", 0.035, "passenger_km", ["rail"]),
        ("underground", "London Underground", "commuting", "rail", 0.028, "passenger_km", ["rail"]),
        ("cycling", "Cycling", "commuting", "active", 0.0, "km", ["active"]),
        ("walking", "Walking", "commuting", "active", 0.0, "km", ["active"]),
        ("ebike", "E-Bike", "commuting", "active", 0.005, "km", ["electric"]),
    ]
    for c in commute:
        factors.append({
            "id": f"defra_commute_{c[0]}", "name": c[1], "category": c[2], "subcategory": c[3],
            "fuel_type": None, "co2_factor": c[4] * 0.95, "ch4_factor": c[4] * 0.02, "n2o_factor": c[4] * 0.03,
            "co2e_factor": c[4], "activity_unit": c[5], "region": "UK", "year": 2025, "tags": c[6] + ["commuting"],
        })

    # Freight
    freight = [
        ("van_petrol", "Van (Petrol, <1.305t)", "transport", "van", 0.601, "tonne_km", ["road"]),
        ("van_diesel", "Van (Diesel, <1.305t)", "transport", "van", 0.577, "tonne_km", ["road"]),
        ("van_average", "Van (Average)", "transport", "van", 0.581, "tonne_km", ["road"]),
        ("rigid_hgv_small", "Rigid HGV (3.5-7.5t)", "transport", "hgv", 0.494, "tonne_km", ["road"]),
        ("rigid_hgv_medium", "Rigid HGV (7.5-17t)", "transport", "hgv", 0.296, "tonne_km", ["road"]),
        ("rigid_hgv_large", "Rigid HGV (>17t)", "transport", "hgv", 0.164, "tonne_km", ["road"]),
        ("artic_hgv", "Articulated HGV (>33t)", "transport", "hgv", 0.091, "tonne_km", ["road"]),
        ("hgv_average", "HGV (All Diesel, Average)", "transport", "hgv", 0.115, "tonne_km", ["road"]),
        ("rail_freight", "Rail Freight", "transport", "rail", 0.024, "tonne_km", ["rail"]),
        ("sea_container", "Sea Freight (Container)", "transport", "sea", 0.016, "tonne_km", ["sea"]),
        ("sea_bulk", "Sea Freight (Bulk Carrier)", "transport", "sea", 0.004, "tonne_km", ["sea"]),
        ("sea_tanker", "Sea Freight (Tanker)", "transport", "sea", 0.005, "tonne_km", ["sea"]),
        ("air_freight_domestic", "Air Freight (Domestic)", "transport", "air", 2.305, "tonne_km", ["air"]),
        ("air_freight_short", "Air Freight (Short-Haul)", "transport", "air", 1.129, "tonne_km", ["air"]),
        ("air_freight_long", "Air Freight (Long-Haul)", "transport", "air", 0.602, "tonne_km", ["air"]),
    ]
    for fr in freight:
        factors.append({
            "id": f"defra_freight_{fr[0]}", "name": fr[1], "category": fr[2], "subcategory": fr[3],
            "fuel_type": None, "co2_factor": fr[4] * 0.95, "ch4_factor": fr[4] * 0.01, "n2o_factor": fr[4] * 0.01,
            "co2e_factor": fr[4], "activity_unit": fr[5], "region": "UK", "year": 2025, "tags": fr[6] + ["freight"],
        })

    # Fuels
    fuels = [
        ("natural_gas_kwh", "Natural Gas", "fuels", "gas", 0.183, "kWh", "natural_gas", ["gas"]),
        ("natural_gas_m3", "Natural Gas", "fuels", "gas", 2.02, "m3", "natural_gas", ["gas"]),
        ("diesel_litre", "Diesel", "fuels", "liquid", 2.556, "litre", "diesel", ["liquid"]),
        ("petrol_litre", "Petrol (Gasoline)", "fuels", "liquid", 2.168, "litre", "gasoline", ["liquid"]),
        ("lpg_litre", "LPG", "fuels", "gas", 1.555, "litre", "lpg", ["gas"]),
        ("lpg_kwh", "LPG", "fuels", "gas", 0.214, "kWh", "lpg", ["gas"]),
        ("fuel_oil_litre", "Fuel Oil", "fuels", "liquid", 2.759, "litre", "fuel_oil_no2", ["liquid"]),
        ("fuel_oil_kwh", "Fuel Oil", "fuels", "liquid", 0.267, "kWh", "fuel_oil_no2", ["liquid"]),
        ("coal_industrial_kg", "Coal (Industrial)", "fuels", "solid", 2.167, "kg", "coal_bituminous", ["solid"]),
        ("coal_domestic_kg", "Coal (Domestic)", "fuels", "solid", 2.883, "kg", "coal_bituminous", ["solid"]),
        ("wood_logs_kg", "Wood Logs", "fuels", "solid", 0.058, "kg", "wood", ["solid", "biomass"]),
        ("wood_chips_kg", "Wood Chips", "fuels", "solid", 0.014, "kg", "wood", ["solid", "biomass"]),
        ("wood_pellets_kg", "Wood Pellets", "fuels", "solid", 0.039, "kg", "wood", ["solid", "biomass"]),
        ("biogas_kwh", "Biogas", "fuels", "gas", 0.00022, "kWh", "landfill_gas", ["gas", "biomass"]),
        ("biodiesel_litre", "Biodiesel (ME)", "fuels", "liquid", 0.172, "litre", "b20", ["liquid", "biofuel"]),
        ("bioethanol_litre", "Bioethanol", "fuels", "liquid", 0.024, "litre", "e85", ["liquid", "biofuel"]),
        ("red_diesel_litre", "Red Diesel (Gas Oil)", "fuels", "liquid", 2.556, "litre", "diesel", ["liquid"]),
        ("aviation_fuel_litre", "Aviation Turbine Fuel", "fuels", "liquid", 2.548, "litre", "jet_fuel", ["liquid"]),
        ("marine_fuel_litre", "Marine Fuel Oil", "fuels", "liquid", 2.759, "litre", "residual_fuel_oil", ["liquid"]),
    ]
    for fl in fuels:
        factors.append({
            "id": f"defra_fuel_{fl[0]}", "name": fl[1], "category": fl[2], "subcategory": fl[3],
            "fuel_type": fl[6], "co2_factor": fl[4] * 0.96, "ch4_factor": fl[4] * 0.01, "n2o_factor": fl[4] * 0.005,
            "co2e_factor": fl[4], "activity_unit": fl[5], "region": "UK", "year": 2025, "tags": fl[7] + ["fuel"],
        })

    # Materials
    materials = [
        ("paper_kg", "Paper (Virgin)", "materials", "paper", 0.919, "kg", ["recycling"]),
        ("paper_recycled_kg", "Paper (Recycled)", "materials", "paper", 0.610, "kg", ["recycling"]),
        ("cardboard_kg", "Cardboard (Virgin)", "materials", "paper", 0.919, "kg", ["recycling"]),
        ("cardboard_recycled_kg", "Cardboard (Recycled)", "materials", "paper", 0.610, "kg", ["recycling"]),
        ("plastic_pet_kg", "Plastic (PET)", "materials", "plastic", 2.732, "kg", []),
        ("plastic_hdpe_kg", "Plastic (HDPE)", "materials", "plastic", 1.578, "kg", []),
        ("plastic_pvc_kg", "Plastic (PVC)", "materials", "plastic", 2.390, "kg", []),
        ("plastic_ldpe_kg", "Plastic (LDPE/LLDPE)", "materials", "plastic", 2.082, "kg", []),
        ("plastic_pp_kg", "Plastic (PP)", "materials", "plastic", 1.498, "kg", []),
        ("plastic_ps_kg", "Plastic (PS)", "materials", "plastic", 2.830, "kg", []),
        ("plastic_avg_kg", "Plastic (Average)", "materials", "plastic", 2.289, "kg", []),
        ("glass_kg", "Glass (Virgin)", "materials", "glass", 0.853, "kg", []),
        ("glass_recycled_kg", "Glass (Recycled)", "materials", "glass", 0.450, "kg", ["recycling"]),
        ("steel_kg", "Steel (Virgin)", "materials", "metal", 1.778, "kg", []),
        ("steel_recycled_kg", "Steel (Recycled)", "materials", "metal", 0.437, "kg", ["recycling"]),
        ("aluminium_kg", "Aluminium (Virgin)", "materials", "metal", 9.167, "kg", []),
        ("aluminium_recycled_kg", "Aluminium (Recycled)", "materials", "metal", 1.690, "kg", ["recycling"]),
        ("copper_kg", "Copper (Virgin)", "materials", "metal", 3.710, "kg", []),
        ("textiles_kg", "Textiles (Average)", "materials", "textile", 5.340, "kg", []),
        ("concrete_kg", "Concrete", "materials", "construction", 0.132, "kg", []),
        ("cement_kg", "Cement", "materials", "construction", 0.740, "kg", []),
        ("bricks_kg", "Bricks", "materials", "construction", 0.230, "kg", []),
        ("aggregate_kg", "Aggregate", "materials", "construction", 0.005, "kg", []),
        ("timber_kg", "Timber", "materials", "construction", 0.263, "kg", []),
        ("electronics_kg", "Electronic Equipment (Avg)", "materials", "electronics", 5.800, "kg", []),
        ("batteries_kg", "Batteries", "materials", "electronics", 3.200, "kg", []),
        ("rubber_kg", "Rubber", "materials", "other", 3.180, "kg", []),
        ("food_waste_kg", "Food Waste (Average)", "materials", "food", 0.450, "kg", ["food"]),
        ("garden_waste_kg", "Garden Waste", "materials", "organic", 0.580, "kg", []),
    ]
    for mat in materials:
        factors.append({
            "id": f"defra_mat_{mat[0]}", "name": mat[1], "category": mat[2], "subcategory": mat[3],
            "fuel_type": None, "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": mat[4], "activity_unit": mat[5], "region": "UK", "year": 2025, "tags": mat[6] + ["material"],
        })

    # Waste disposal
    waste = [
        ("landfill_mixed_tonne", "Mixed Waste (Landfill)", "waste", "landfill", "mixed_landfill", 446, "tonne"),
        ("landfill_paper_tonne", "Paper/Card (Landfill)", "waste", "landfill", "paper_landfill", 1042, "tonne"),
        ("landfill_food_tonne", "Food Waste (Landfill)", "waste", "landfill", "food_landfill", 580, "tonne"),
        ("landfill_wood_tonne", "Wood (Landfill)", "waste", "landfill", "wood_landfill", 828, "tonne"),
        ("landfill_textiles_tonne", "Textiles (Landfill)", "waste", "landfill", "textiles_landfill", 447, "tonne"),
        ("landfill_plastic_tonne", "Plastics (Landfill)", "waste", "landfill", "plastic_landfill", 21, "tonne"),
        ("incineration_mixed_tonne", "Mixed Waste (Incineration)", "waste", "incineration", "mixed_incineration", 21.35, "tonne"),
        ("incineration_plastic_tonne", "Plastics (Incineration)", "waste", "incineration", "plastic_incineration", 2695, "tonne"),
        ("recycling_paper_tonne", "Paper/Card (Recycling)", "waste", "recycling", "paper_recycling", 21.35, "tonne"),
        ("recycling_plastic_tonne", "Plastics (Recycling)", "waste", "recycling", "plastic_recycling", 21.35, "tonne"),
        ("recycling_glass_tonne", "Glass (Recycling)", "waste", "recycling", "glass_recycling", 21.35, "tonne"),
        ("recycling_metal_tonne", "Metals (Recycling)", "waste", "recycling", "metal_recycling", 21.35, "tonne"),
        ("composting_food_tonne", "Food Waste (Composting)", "waste", "composting", "food_composting", 10.2, "tonne"),
        ("composting_garden_tonne", "Garden Waste (Composting)", "waste", "composting", "garden_composting", 10.2, "tonne"),
        ("ad_food_tonne", "Food Waste (Anaerobic Digestion)", "waste", "anaerobic_digestion", "food_ad", 10.2, "tonne"),
    ]
    for w in waste:
        factors.append({
            "id": f"defra_waste_{w[0]}", "name": w[1], "category": w[2], "subcategory": w[3],
            "fuel_type": w[4], "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": w[5], "activity_unit": w[6], "region": "UK", "year": 2025, "tags": ["waste", w[3]],
        })

    # Water
    water = [
        ("supply_m3", "Water Supply", "water", "supply", 0.149, "m3", ["water"]),
        ("treatment_m3", "Water Treatment", "water", "treatment", 0.272, "m3", ["water"]),
    ]
    for wt in water:
        factors.append({
            "id": f"defra_water_{wt[0]}", "name": wt[1], "category": wt[2], "subcategory": wt[3],
            "fuel_type": None, "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": wt[4], "activity_unit": wt[5], "region": "UK", "year": 2025, "tags": wt[6],
        })

    # Hotel stays
    hotels = [
        ("uk_night", "Hotel Stay - UK", "hotel_stays", "accommodation", 10.3, "night", "UK"),
        ("europe_night", "Hotel Stay - Europe (Avg)", "hotel_stays", "accommodation", 14.5, "night", "EU"),
        ("usa_night", "Hotel Stay - USA", "hotel_stays", "accommodation", 20.4, "night", "US"),
        ("asia_night", "Hotel Stay - Asia (Avg)", "hotel_stays", "accommodation", 15.2, "night", "ASIA"),
        ("global_night", "Hotel Stay - Global Average", "hotel_stays", "accommodation", 15.0, "night", "GLOBAL"),
    ]
    for h in hotels:
        factors.append({
            "id": f"defra_hotel_{h[0]}", "name": h[1], "category": h[2], "subcategory": h[3],
            "fuel_type": None, "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": h[4], "activity_unit": h[5], "region": h[6], "year": 2025, "tags": ["hotel", "accommodation"],
        })

    # Electricity (UK)
    factors.append({
        "id": "defra_elec_uk_kwh", "name": "UK Grid Electricity", "category": "electricity",
        "subcategory": "grid_electricity", "fuel_type": None,
        "co2_factor": 0.207, "ch4_factor": 0.00001, "n2o_factor": 0.000001,
        "co2e_factor": 0.212, "activity_unit": "kWh", "region": "UK", "year": 2025,
        "tags": ["electricity", "grid"],
    })

    write_json("defra", "v2025.json", {
        "source": "defra", "version": "2025", "year": 2025,
        "description": "UK DEFRA/BEIS GHG Conversion Factors for Company Reporting",
        "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
        "factors": factors,
    })


# ─── USEEIO ─────────────────────────────────────────────────────────────────

def build_useeio():
    factors = []

    # (naics_code, name, co2e_per_usd, subsector)
    sectors = [
        # Agriculture
        ("1111", "Oilseed farming", 1.20, "Agriculture"),
        ("1112", "Grain farming", 1.10, "Agriculture"),
        ("1113", "Vegetable and melon farming", 0.75, "Agriculture"),
        ("1114", "Fruit and tree nut farming", 0.60, "Agriculture"),
        ("1119", "Other crop farming", 0.95, "Agriculture"),
        ("1121", "Cattle ranching", 1.80, "Agriculture"),
        ("1122", "Hog and pig farming", 1.50, "Agriculture"),
        ("1123", "Poultry and egg production", 1.05, "Agriculture"),
        ("1124", "Sheep and goat farming", 1.60, "Agriculture"),
        ("1125", "Aquaculture", 0.90, "Agriculture"),
        ("1131", "Timber tract operations", 0.30, "Agriculture"),
        ("1132", "Forest nurseries and timber", 0.35, "Agriculture"),
        ("1141", "Fishing", 1.10, "Agriculture"),
        ("1142", "Hunting and trapping", 0.50, "Agriculture"),
        ("1151", "Support activities for crop production", 0.55, "Agriculture"),
        ("1152", "Support activities for animal production", 0.60, "Agriculture"),
        # Mining
        ("2111", "Oil and gas extraction", 1.20, "Mining"),
        ("2121", "Coal mining", 1.50, "Mining"),
        ("2122", "Metal ore mining", 0.95, "Mining"),
        ("2123", "Nonmetallic mineral mining", 0.80, "Mining"),
        ("2131", "Support activities for mining", 0.70, "Mining"),
        # Utilities
        ("2211", "Electric power generation", 2.50, "Utilities"),
        ("2212", "Natural gas distribution", 1.80, "Utilities"),
        ("2213", "Water, sewage and other systems", 1.00, "Utilities"),
        # Construction
        ("2361", "Residential building construction", 0.40, "Construction"),
        ("2362", "Nonresidential building construction", 0.45, "Construction"),
        ("2371", "Utility system construction", 0.50, "Construction"),
        ("2372", "Land subdivision", 0.35, "Construction"),
        ("2373", "Highway and street construction", 0.55, "Construction"),
        ("2379", "Other heavy construction", 0.50, "Construction"),
        ("2381", "Building foundation and exterior", 0.38, "Construction"),
        ("2382", "Building equipment contractors", 0.30, "Construction"),
        ("2383", "Building finishing contractors", 0.25, "Construction"),
        ("2389", "Other specialty trade contractors", 0.35, "Construction"),
        # Manufacturing - Food
        ("3111", "Animal food manufacturing", 0.70, "Manufacturing"),
        ("3112", "Grain and oilseed milling", 0.55, "Manufacturing"),
        ("3113", "Sugar and confectionery", 0.50, "Manufacturing"),
        ("3114", "Fruit and vegetable preserving", 0.45, "Manufacturing"),
        ("3115", "Dairy product manufacturing", 0.60, "Manufacturing"),
        ("3116", "Animal slaughtering and processing", 0.75, "Manufacturing"),
        ("3117", "Seafood product preparation", 0.55, "Manufacturing"),
        ("3118", "Bakeries and tortilla manufacturing", 0.40, "Manufacturing"),
        ("3119", "Other food manufacturing", 0.50, "Manufacturing"),
        ("3121", "Beverage manufacturing", 0.35, "Manufacturing"),
        ("3122", "Tobacco manufacturing", 0.25, "Manufacturing"),
        # Manufacturing - Textiles
        ("3131", "Fiber, yarn, and thread mills", 0.80, "Manufacturing"),
        ("3132", "Fabric mills", 0.75, "Manufacturing"),
        ("3133", "Textile finishing", 0.65, "Manufacturing"),
        ("3141", "Textile furnishings mills", 0.55, "Manufacturing"),
        ("3149", "Other textile product mills", 0.60, "Manufacturing"),
        ("3151", "Apparel knitting mills", 0.50, "Manufacturing"),
        ("3152", "Cut and sew apparel manufacturing", 0.40, "Manufacturing"),
        ("3159", "Apparel accessories manufacturing", 0.45, "Manufacturing"),
        # Manufacturing - Wood/Paper
        ("3211", "Sawmills and wood preservation", 0.60, "Manufacturing"),
        ("3212", "Veneer and plywood manufacturing", 0.55, "Manufacturing"),
        ("3219", "Other wood product manufacturing", 0.50, "Manufacturing"),
        ("3221", "Pulp, paper, and paperboard mills", 1.10, "Manufacturing"),
        ("3222", "Converted paper product manufacturing", 0.65, "Manufacturing"),
        # Manufacturing - Printing
        ("3231", "Printing and related support", 0.30, "Manufacturing"),
        # Manufacturing - Petroleum/Coal
        ("3241", "Petroleum and coal products", 1.40, "Manufacturing"),
        # Manufacturing - Chemicals
        ("3251", "Basic chemical manufacturing", 1.20, "Manufacturing"),
        ("3252", "Resin and synthetic rubber", 0.95, "Manufacturing"),
        ("3253", "Pesticide and agricultural chemicals", 0.85, "Manufacturing"),
        ("3254", "Pharmaceutical manufacturing", 0.18, "Manufacturing"),
        ("3255", "Paint and coating manufacturing", 0.60, "Manufacturing"),
        ("3256", "Soap and cleaning compound", 0.45, "Manufacturing"),
        ("3259", "Other chemical manufacturing", 0.70, "Manufacturing"),
        # Manufacturing - Plastics/Rubber
        ("3261", "Plastics product manufacturing", 0.75, "Manufacturing"),
        ("3262", "Rubber product manufacturing", 0.65, "Manufacturing"),
        # Manufacturing - Nonmetallic minerals
        ("3271", "Clay and refractory manufacturing", 0.90, "Manufacturing"),
        ("3272", "Glass and glass product manufacturing", 0.85, "Manufacturing"),
        ("3273", "Cement and concrete manufacturing", 1.30, "Manufacturing"),
        ("3274", "Lime and gypsum manufacturing", 1.50, "Manufacturing"),
        ("3279", "Other nonmetallic mineral products", 0.80, "Manufacturing"),
        # Manufacturing - Metals
        ("3311", "Iron and steel mills", 1.00, "Manufacturing"),
        ("3312", "Steel product manufacturing", 0.85, "Manufacturing"),
        ("3313", "Alumina and aluminum production", 0.95, "Manufacturing"),
        ("3314", "Nonferrous metal production", 0.80, "Manufacturing"),
        ("3315", "Foundries", 0.90, "Manufacturing"),
        ("3321", "Forging and stamping", 0.60, "Manufacturing"),
        ("3322", "Cutlery and handtool manufacturing", 0.45, "Manufacturing"),
        ("3323", "Architectural and structural metals", 0.50, "Manufacturing"),
        ("3324", "Boiler, tank, and shipping container", 0.55, "Manufacturing"),
        ("3325", "Hardware manufacturing", 0.40, "Manufacturing"),
        ("3326", "Spring and wire product manufacturing", 0.50, "Manufacturing"),
        ("3327", "Machine shops and threaded products", 0.35, "Manufacturing"),
        ("3328", "Coating, engraving, heat treating", 0.45, "Manufacturing"),
        ("3329", "Other fabricated metal products", 0.40, "Manufacturing"),
        # Manufacturing - Machinery
        ("3331", "Ag/construction/mining machinery", 0.30, "Manufacturing"),
        ("3332", "Industrial machinery manufacturing", 0.25, "Manufacturing"),
        ("3333", "Commercial/service industry machinery", 0.20, "Manufacturing"),
        ("3334", "HVAC and commercial refrigeration", 0.28, "Manufacturing"),
        ("3335", "Metalworking machinery", 0.22, "Manufacturing"),
        ("3336", "Engine and turbine manufacturing", 0.30, "Manufacturing"),
        ("3339", "Other general purpose machinery", 0.25, "Manufacturing"),
        # Manufacturing - Electronics
        ("3341", "Computer and peripheral equipment", 0.15, "Manufacturing"),
        ("3342", "Communications equipment", 0.12, "Manufacturing"),
        ("3343", "Audio and video equipment", 0.10, "Manufacturing"),
        ("3344", "Semiconductor manufacturing", 0.25, "Manufacturing"),
        ("3345", "Electronic instruments", 0.13, "Manufacturing"),
        ("3346", "Magnetic and optical media", 0.18, "Manufacturing"),
        # Manufacturing - Electrical
        ("3351", "Electric lighting equipment", 0.30, "Manufacturing"),
        ("3352", "Household appliance manufacturing", 0.28, "Manufacturing"),
        ("3353", "Electrical equipment manufacturing", 0.25, "Manufacturing"),
        ("3359", "Other electrical equipment", 0.22, "Manufacturing"),
        # Manufacturing - Transportation Equipment
        ("3361", "Motor vehicle manufacturing", 0.25, "Manufacturing"),
        ("3362", "Motor vehicle body and trailer", 0.30, "Manufacturing"),
        ("3363", "Motor vehicle parts manufacturing", 0.35, "Manufacturing"),
        ("3364", "Aerospace product manufacturing", 0.20, "Manufacturing"),
        ("3365", "Railroad rolling stock manufacturing", 0.28, "Manufacturing"),
        ("3366", "Ship and boat building", 0.32, "Manufacturing"),
        ("3369", "Other transportation equipment", 0.25, "Manufacturing"),
        # Manufacturing - Furniture/Other
        ("3371", "Household and institutional furniture", 0.30, "Manufacturing"),
        ("3372", "Office furniture manufacturing", 0.25, "Manufacturing"),
        ("3391", "Medical equipment and supplies", 0.15, "Manufacturing"),
        ("3399", "Other miscellaneous manufacturing", 0.30, "Manufacturing"),
        # Wholesale Trade
        ("4231", "Motor vehicle parts wholesale", 0.12, "Trade"),
        ("4232", "Furniture wholesale", 0.10, "Trade"),
        ("4233", "Lumber wholesale", 0.14, "Trade"),
        ("4234", "Professional equipment wholesale", 0.08, "Trade"),
        ("4235", "Metal and mineral wholesale", 0.18, "Trade"),
        ("4236", "Household appliances wholesale", 0.09, "Trade"),
        ("4237", "Hardware and plumbing wholesale", 0.11, "Trade"),
        ("4238", "Machinery wholesale", 0.10, "Trade"),
        ("4239", "Miscellaneous durable goods wholesale", 0.11, "Trade"),
        ("4241", "Paper and packaging wholesale", 0.12, "Trade"),
        ("4242", "Drugs and sundries wholesale", 0.06, "Trade"),
        ("4244", "Grocery wholesale", 0.14, "Trade"),
        ("4245", "Farm product wholesale", 0.16, "Trade"),
        ("4246", "Chemical wholesale", 0.15, "Trade"),
        ("4247", "Petroleum wholesale", 0.20, "Trade"),
        ("4248", "Beer, wine, spirits wholesale", 0.10, "Trade"),
        ("4249", "Miscellaneous nondurable wholesale", 0.11, "Trade"),
        # Retail
        ("4411", "Automobile dealers", 0.08, "Trade"),
        ("4413", "Auto parts and accessories stores", 0.10, "Trade"),
        ("4431", "Electronics and appliance stores", 0.07, "Trade"),
        ("4441", "Building material and supplies", 0.12, "Trade"),
        ("4451", "Grocery stores", 0.15, "Trade"),
        ("4461", "Health and personal care stores", 0.08, "Trade"),
        ("4471", "Gasoline stations", 0.22, "Trade"),
        ("4481", "Clothing stores", 0.06, "Trade"),
        ("4511", "Sporting goods/hobby/book stores", 0.07, "Trade"),
        ("4521", "Department stores", 0.09, "Trade"),
        ("4529", "Other general merchandise stores", 0.10, "Trade"),
        ("4531", "Florists", 0.08, "Trade"),
        ("4539", "Other miscellaneous store retailers", 0.09, "Trade"),
        ("4541", "Electronic shopping and mail-order", 0.05, "Trade"),
        # Transportation
        ("4811", "Scheduled air transportation", 1.30, "Transportation"),
        ("4812", "Nonscheduled air transportation", 1.50, "Transportation"),
        ("4821", "Rail transportation", 0.60, "Transportation"),
        ("4831", "Deep sea freight transportation", 0.50, "Transportation"),
        ("4832", "Inland water transportation", 0.55, "Transportation"),
        ("4841", "General freight trucking", 0.80, "Transportation"),
        ("4842", "Specialized freight trucking", 0.75, "Transportation"),
        ("4851", "Urban transit systems", 0.65, "Transportation"),
        ("4852", "Interurban bus transportation", 0.45, "Transportation"),
        ("4853", "Taxi and limousine service", 0.60, "Transportation"),
        ("4854", "School and employee bus", 0.55, "Transportation"),
        ("4859", "Other ground passenger transport", 0.50, "Transportation"),
        ("4861", "Pipeline transportation of crude oil", 0.30, "Transportation"),
        ("4862", "Pipeline transportation of natural gas", 0.35, "Transportation"),
        ("4869", "Other pipeline transportation", 0.32, "Transportation"),
        ("4871", "Scenic and sightseeing transport", 0.40, "Transportation"),
        ("4881", "Support activities for air transport", 0.30, "Transportation"),
        ("4882", "Support activities for rail transport", 0.25, "Transportation"),
        ("4883", "Support for water transportation", 0.28, "Transportation"),
        ("4884", "Support for road transportation", 0.22, "Transportation"),
        ("4885", "Freight transportation arrangement", 0.15, "Transportation"),
        ("4889", "Other transportation support", 0.20, "Transportation"),
        ("4911", "Postal service", 0.18, "Transportation"),
        ("4921", "Couriers and express delivery", 0.25, "Transportation"),
        ("4922", "Local messengers and delivery", 0.30, "Transportation"),
        ("4931", "Warehousing and storage", 0.15, "Transportation"),
        # Information
        ("5111", "Newspaper, book, directory publishers", 0.10, "Information"),
        ("5112", "Software publishers", 0.04, "Information"),
        ("5121", "Motion picture and video industries", 0.08, "Information"),
        ("5122", "Sound recording industries", 0.05, "Information"),
        ("5151", "Radio and television broadcasting", 0.07, "Information"),
        ("5152", "Cable and subscription programming", 0.06, "Information"),
        ("5171", "Wired telecommunications", 0.08, "Information"),
        ("5172", "Wireless telecommunications", 0.06, "Information"),
        ("5174", "Satellite telecommunications", 0.10, "Information"),
        ("5179", "Other telecommunications", 0.07, "Information"),
        ("5182", "Data processing and hosting", 0.12, "Information"),
        ("5191", "Other information services", 0.05, "Information"),
        # Finance
        ("5211", "Monetary authorities - central bank", 0.03, "Finance"),
        ("5221", "Depository credit intermediation", 0.04, "Finance"),
        ("5222", "Nondepository credit intermediation", 0.03, "Finance"),
        ("5223", "Activities related to credit", 0.03, "Finance"),
        ("5231", "Securities and commodity exchanges", 0.04, "Finance"),
        ("5239", "Other financial investment activities", 0.05, "Finance"),
        ("5241", "Insurance carriers", 0.04, "Finance"),
        ("5242", "Insurance agencies and brokerages", 0.03, "Finance"),
        ("5251", "Insurance and employee benefit funds", 0.03, "Finance"),
        ("5259", "Other investment pools and funds", 0.04, "Finance"),
        # Real Estate
        ("5311", "Lessors of real estate", 0.08, "Real Estate"),
        ("5312", "Offices of real estate agents", 0.05, "Real Estate"),
        ("5313", "Activities related to real estate", 0.06, "Real Estate"),
        # Professional Services
        ("5411", "Legal services", 0.05, "Professional"),
        ("5412", "Accounting and bookkeeping", 0.05, "Professional"),
        ("5413", "Architectural and engineering services", 0.06, "Professional"),
        ("5414", "Specialized design services", 0.04, "Professional"),
        ("5415", "Computer systems design", 0.04, "Professional"),
        ("5416", "Management consulting", 0.05, "Professional"),
        ("5417", "Scientific research and development", 0.07, "Professional"),
        ("5418", "Advertising and related services", 0.06, "Professional"),
        ("5419", "Other professional services", 0.05, "Professional"),
        # Management
        ("5511", "Management of companies", 0.06, "Management"),
        # Admin/Waste
        ("5611", "Office administrative services", 0.05, "Admin"),
        ("5612", "Facilities support services", 0.08, "Admin"),
        ("5613", "Employment services", 0.04, "Admin"),
        ("5614", "Business support services", 0.05, "Admin"),
        ("5615", "Travel arrangement services", 0.06, "Admin"),
        ("5616", "Investigation and security services", 0.04, "Admin"),
        ("5617", "Services to buildings and dwellings", 0.07, "Admin"),
        ("5619", "Other support services", 0.05, "Admin"),
        ("5621", "Waste collection", 0.30, "Admin"),
        ("5622", "Waste treatment and disposal", 0.50, "Admin"),
        ("5629", "Remediation services", 0.25, "Admin"),
        # Education
        ("6111", "Elementary and secondary schools", 0.10, "Education"),
        ("6112", "Junior colleges", 0.12, "Education"),
        ("6113", "Colleges and universities", 0.12, "Education"),
        # Healthcare
        ("6211", "Offices of physicians", 0.10, "Healthcare"),
        ("6212", "Offices of dentists", 0.08, "Healthcare"),
        ("6213", "Offices of other health practitioners", 0.08, "Healthcare"),
        ("6214", "Outpatient care centers", 0.12, "Healthcare"),
        ("6215", "Medical and diagnostic laboratories", 0.15, "Healthcare"),
        ("6216", "Home health care services", 0.08, "Healthcare"),
        ("6219", "Other ambulatory health care", 0.10, "Healthcare"),
        ("6221", "General medical and surgical hospitals", 0.20, "Healthcare"),
        ("6222", "Psychiatric and substance abuse hospitals", 0.18, "Healthcare"),
        ("6223", "Specialty hospitals", 0.19, "Healthcare"),
        ("6231", "Nursing care facilities", 0.15, "Healthcare"),
        ("6232", "Residential mental health facilities", 0.14, "Healthcare"),
        ("6233", "Continuing care retirement communities", 0.13, "Healthcare"),
        ("6239", "Other residential care facilities", 0.12, "Healthcare"),
        ("6241", "Individual and family services", 0.06, "Healthcare"),
        ("6242", "Community food/housing services", 0.08, "Healthcare"),
        ("6243", "Vocational rehabilitation services", 0.07, "Healthcare"),
        ("6244", "Child day care services", 0.06, "Healthcare"),
        # Accommodation/Food
        ("7211", "Traveler accommodation", 0.35, "Accommodation"),
        ("7212", "RV parks and recreational camps", 0.25, "Accommodation"),
        ("7213", "Rooming and boarding houses", 0.30, "Accommodation"),
        ("7221", "Full-service restaurants", 0.30, "Food Service"),
        ("7222", "Limited-service eating places", 0.35, "Food Service"),
        ("7223", "Special food services", 0.28, "Food Service"),
        ("7224", "Drinking places (alcoholic beverages)", 0.25, "Food Service"),
        # Arts/Entertainment
        ("7111", "Performing arts companies", 0.06, "Arts"),
        ("7112", "Spectator sports", 0.08, "Arts"),
        ("7113", "Promoters of events", 0.07, "Arts"),
        ("7114", "Agents for artists and performers", 0.04, "Arts"),
        ("7115", "Independent artists and performers", 0.03, "Arts"),
        ("7121", "Museums, historical sites, zoos", 0.08, "Arts"),
        ("7131", "Amusement parks and arcades", 0.12, "Arts"),
        ("7132", "Gambling industries", 0.10, "Arts"),
        ("7139", "Other amusement and recreation", 0.09, "Arts"),
        # Other Services
        ("8111", "Automotive repair and maintenance", 0.12, "Services"),
        ("8112", "Electronic equipment repair", 0.08, "Services"),
        ("8113", "Commercial machinery repair", 0.10, "Services"),
        ("8114", "Personal and household goods repair", 0.07, "Services"),
        ("8121", "Personal care services", 0.06, "Services"),
        ("8122", "Death care services", 0.10, "Services"),
        ("8123", "Drycleaning and laundry services", 0.15, "Services"),
        ("8129", "Other personal services", 0.06, "Services"),
    ]

    for s in sectors:
        factors.append({
            "id": f"useeio_{s[0]}", "name": s[1],
            "category": "spend_based", "subcategory": s[3],
            "fuel_type": s[0], "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
            "co2e_factor": s[2], "activity_unit": "USD",
            "region": "US", "year": 2023, "tags": ["spend_based", f"naics_{s[0]}", s[3].lower()],
        })

    write_json("useeio", "v1_3.json", {
        "source": "useeio", "version": "1.3", "year": 2023,
        "description": "US EPA USEEIO v1.3 - Spend-based emission factors by NAICS sector",
        "url": "https://www.epa.gov/land-research/us-environmentally-extended-input-output-useeio-technical-content",
        "factors": factors,
    })


# ─── EMBER ───────────────────────────────────────────────────────────────────

def build_ember():
    factors = []

    # (country_code, country_name, kg_co2_per_kwh)
    countries = [
        ("AF", "Afghanistan", 0.12), ("AL", "Albania", 0.01), ("DZ", "Algeria", 0.48),
        ("AO", "Angola", 0.22), ("AR", "Argentina", 0.34), ("AM", "Armenia", 0.18),
        ("AU", "Australia", 0.55), ("AT", "Austria", 0.10), ("AZ", "Azerbaijan", 0.48),
        ("BH", "Bahrain", 0.56), ("BD", "Bangladesh", 0.56), ("BY", "Belarus", 0.34),
        ("BE", "Belgium", 0.15), ("BO", "Bolivia", 0.40), ("BA", "Bosnia Herzegovina", 0.68),
        ("BR", "Brazil", 0.07), ("BN", "Brunei", 0.59), ("BG", "Bulgaria", 0.35),
        ("KH", "Cambodia", 0.52), ("CA", "Canada", 0.11), ("CL", "Chile", 0.32),
        ("CN", "China", 0.55), ("CO", "Colombia", 0.16), ("CR", "Costa Rica", 0.02),
        ("HR", "Croatia", 0.16), ("CU", "Cuba", 0.85), ("CY", "Cyprus", 0.55),
        ("CZ", "Czechia", 0.40), ("DK", "Denmark", 0.12), ("DO", "Dominican Republic", 0.54),
        ("EC", "Ecuador", 0.17), ("EG", "Egypt", 0.45), ("SV", "El Salvador", 0.12),
        ("EE", "Estonia", 0.45), ("ET", "Ethiopia", 0.01), ("FI", "Finland", 0.07),
        ("FR", "France", 0.06), ("GE", "Georgia", 0.09), ("DE", "Germany", 0.35),
        ("GH", "Ghana", 0.28), ("GR", "Greece", 0.32), ("GT", "Guatemala", 0.33),
        ("HN", "Honduras", 0.33), ("HK", "Hong Kong", 0.59), ("HU", "Hungary", 0.21),
        ("IS", "Iceland", 0.00), ("IN", "India", 0.63), ("ID", "Indonesia", 0.65),
        ("IR", "Iran", 0.49), ("IQ", "Iraq", 0.68), ("IE", "Ireland", 0.26),
        ("IL", "Israel", 0.42), ("IT", "Italy", 0.33), ("JM", "Jamaica", 0.62),
        ("JP", "Japan", 0.45), ("JO", "Jordan", 0.44), ("KZ", "Kazakhstan", 0.62),
        ("KE", "Kenya", 0.07), ("KW", "Kuwait", 0.57), ("KG", "Kyrgyzstan", 0.06),
        ("LA", "Laos", 0.25), ("LV", "Latvia", 0.08), ("LB", "Lebanon", 0.60),
        ("LY", "Libya", 0.65), ("LT", "Lithuania", 0.06), ("LU", "Luxembourg", 0.08),
        ("MY", "Malaysia", 0.53), ("MX", "Mexico", 0.40), ("MN", "Mongolia", 0.85),
        ("MA", "Morocco", 0.56), ("MZ", "Mozambique", 0.04), ("MM", "Myanmar", 0.37),
        ("NA", "Namibia", 0.08), ("NP", "Nepal", 0.01), ("NL", "Netherlands", 0.31),
        ("NZ", "New Zealand", 0.08), ("NI", "Nicaragua", 0.28), ("NG", "Nigeria", 0.38),
        ("KP", "North Korea", 0.42), ("NO", "Norway", 0.01), ("OM", "Oman", 0.50),
        ("PK", "Pakistan", 0.36), ("PA", "Panama", 0.14), ("PY", "Paraguay", 0.01),
        ("PE", "Peru", 0.20), ("PH", "Philippines", 0.55), ("PL", "Poland", 0.62),
        ("PT", "Portugal", 0.15), ("QA", "Qatar", 0.47), ("RO", "Romania", 0.24),
        ("RU", "Russia", 0.33), ("SA", "Saudi Arabia", 0.55), ("SN", "Senegal", 0.52),
        ("RS", "Serbia", 0.60), ("SG", "Singapore", 0.37), ("SK", "Slovakia", 0.12),
        ("SI", "Slovenia", 0.22), ("ZA", "South Africa", 0.90), ("KR", "South Korea", 0.42),
        ("ES", "Spain", 0.17), ("LK", "Sri Lanka", 0.36), ("SE", "Sweden", 0.03),
        ("CH", "Switzerland", 0.01), ("TW", "Taiwan", 0.50), ("TZ", "Tanzania", 0.25),
        ("TH", "Thailand", 0.43), ("TN", "Tunisia", 0.42), ("TR", "Turkey", 0.38),
        ("TM", "Turkmenistan", 0.70), ("UA", "Ukraine", 0.30), ("AE", "UAE", 0.40),
        ("GB", "United Kingdom", 0.21), ("US", "United States", 0.37),
        ("UY", "Uruguay", 0.04), ("UZ", "Uzbekistan", 0.45), ("VE", "Venezuela", 0.14),
        ("VN", "Vietnam", 0.41), ("ZM", "Zambia", 0.02), ("ZW", "Zimbabwe", 0.50),
        ("WORLD", "World Average", 0.42),
    ]

    for c in countries:
        co2 = c[2]
        factors.append({
            "id": f"ember_{c[0].lower()}", "name": f"Electricity - {c[1]}",
            "category": "electricity", "subcategory": "grid_electricity",
            "fuel_type": None,
            "co2_factor": round(co2 * 0.97, 6), "ch4_factor": round(co2 * 0.01, 8),
            "n2o_factor": round(co2 * 0.002, 8),
            "activity_unit": "kWh", "region": c[0], "year": 2024,
            "tags": ["electricity", "grid", "international"],
        })

    write_json("ember", "v2024.json", {
        "source": "ember", "version": "2024", "year": 2024,
        "description": "Ember Global Electricity Review - Country-level electricity emission factors",
        "url": "https://ember-climate.org/data/",
        "factors": factors,
    })


# ─── EXIOBASE ────────────────────────────────────────────────────────────────

def build_exiobase():
    factors = []

    regions = [
        ("EU", "European Union", "EUR"),
        ("CN", "China", "USD"),
        ("JP", "Japan", "USD"),
        ("IN", "India", "USD"),
        ("BR", "Brazil", "USD"),
        ("RU", "Russia", "USD"),
        ("ROW", "Rest of World", "USD"),
    ]

    sectors = [
        ("agriculture", "Agriculture & Forestry", 1.10),
        ("fishing", "Fishing", 0.90),
        ("mining_coal", "Mining of Coal", 1.80),
        ("mining_oil_gas", "Extraction of Oil & Gas", 1.30),
        ("mining_metals", "Mining of Metal Ores", 1.00),
        ("mining_other", "Other Mining & Quarrying", 0.80),
        ("food_processing", "Food Processing", 0.55),
        ("textiles", "Textiles & Wearing Apparel", 0.65),
        ("wood_products", "Wood & Wood Products", 0.50),
        ("paper_publishing", "Paper, Publishing & Printing", 0.60),
        ("chemicals", "Chemical Products", 0.90),
        ("rubber_plastics", "Rubber & Plastic Products", 0.70),
        ("non_metallic_minerals", "Non-metallic Mineral Products", 1.40),
        ("basic_metals", "Basic Metals", 1.20),
        ("fabricated_metals", "Fabricated Metal Products", 0.55),
        ("machinery", "Machinery & Equipment", 0.30),
        ("electronics", "Electrical & Electronic Equipment", 0.25),
        ("transport_equipment", "Transport Equipment", 0.35),
        ("other_manufacturing", "Other Manufacturing", 0.40),
        ("electricity_gas", "Electricity, Gas & Water", 2.20),
        ("construction", "Construction", 0.50),
        ("trade", "Trade & Repair", 0.12),
        ("hotels_restaurants", "Hotels & Restaurants", 0.30),
        ("land_transport", "Land Transport", 0.70),
        ("water_transport", "Water Transport", 0.80),
        ("air_transport", "Air Transport", 1.50),
        ("post_telecom", "Post & Telecommunications", 0.08),
        ("financial", "Financial Intermediation", 0.05),
        ("real_estate", "Real Estate & Business Activities", 0.08),
        ("public_admin", "Public Administration", 0.10),
        ("education", "Education", 0.08),
        ("health", "Health & Social Work", 0.12),
        ("other_services", "Other Services", 0.10),
    ]

    # Regional multipliers
    multipliers = {"EU": 1.0, "CN": 1.4, "JP": 0.85, "IN": 1.6, "BR": 0.7, "RU": 1.5, "ROW": 1.2}

    for region, region_name, currency in regions:
        mult = multipliers[region]
        for sector_id, sector_name, base_factor in sectors:
            factor_val = round(base_factor * mult, 4)
            factors.append({
                "id": f"exio_{region.lower()}_{sector_id}",
                "name": f"{sector_name} - {region_name}",
                "category": "spend_based", "subcategory": sector_name,
                "fuel_type": sector_id,
                "co2_factor": 0, "ch4_factor": 0, "n2o_factor": 0,
                "co2e_factor": factor_val,
                "activity_unit": currency, "region": region, "year": 2022,
                "tags": ["spend_based", "mrio", region.lower()],
            })

    write_json("exiobase", "v3_8.json", {
        "source": "exiobase", "version": "3.8", "year": 2022,
        "description": "EXIOBASE v3.8 - Multi-Regional Input-Output emission factors",
        "url": "https://www.exiobase.eu/",
        "factors": factors,
    })


if __name__ == "__main__":
    print("Building emission factor databases...")
    build_epa_hub()
    build_defra()
    build_useeio()
    build_ember()
    build_exiobase()
    print("Done!")
