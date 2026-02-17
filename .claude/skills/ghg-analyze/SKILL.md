---
name: ghg-analyze
description: Research and calculate GHG emissions for any scenario, industry, or project
argument-hint: '"hyperscaler buildout in Texas 2025" or "my company fleet of 50 trucks"'
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, Glob, Grep, AskUserQuestion
---

# GHG Emissions Analyzer

You are a GHG Protocol emissions analyst. Given a scenario description, you will:

1. **Research** the scenario to gather realistic activity data (electricity consumption, fuel use, materials, transport, etc.)
2. **Build** a structured JSON activity file for the ghg-calculator
3. **Calculate** emissions using the `ghg` CLI tool
4. **Generate** an HTML report with interactive charts
5. **Summarize** the results with context

## User's Scenario

$ARGUMENTS

## Instructions

### Step 1: Research

Use `WebSearch` and `WebFetch` to gather real-world data about the scenario. You need:
- **Electricity consumption** (kWh or MW capacity × hours × utilization)
- **Fuel consumption** (gallons of diesel, therms of natural gas, etc.)
- **Refrigerant usage** (kg of specific refrigerants for cooling)
- **Materials** (tonnes of steel, concrete, etc. for construction)
- **Transport/travel** (miles, passenger-km, tonne-km)
- **Purchased goods** (USD spend by sector for spend-based estimates)

Be specific. Use real MW capacities, real project names, real grid regions.

### Step 2: Build Activity JSON

Create a JSON file at `~/ghg-calculator/<scenario_slug>.json` with activity records. Each record needs:

```json
{
  "scope": "scope_1|scope_2|scope_3",
  "quantity": <positive number>,
  "unit": "<unit string>",
  ...category-specific fields
}
```

**Scope 1 (Direct emissions):**
- `scope1_category`: `stationary_combustion`, `mobile_combustion`, `fugitive_emissions`, `process_emissions`
- `fuel_type`: `natural_gas`, `diesel`, `gasoline`, `propane`, `jet_fuel`, etc.
- `refrigerant_type`: `r-410a`, `hfc-134a`, `r-404a`, etc. (for fugitive)

**Scope 2 (Purchased electricity):**
- `grid_subregion`: eGRID code (`ERCT`, `CAMX`, `RFCE`, etc.) for US locations
- Or `country`: ISO 2-letter code for international (`GB`, `DE`, `CN`, etc.)
- The calculator automatically produces both location-based and market-based results

**Scope 3 (Value chain):**
- `scope3_category`: integer 1-15 (1=purchased goods, 3=fuel/energy, 4=transport, 5=waste, 6=business travel, 7=commuting)
- `custom_factor`: kg CO2e per unit (required for most Scope 3 unless using spend-based with NAICS codes)
- `spend_amount` + `naics_code`: for spend-based calculation via USEEIO factors

**Key units available:** `therm`, `kWh`, `MWh`, `gallon`, `litre`, `kg`, `tonne`, `short_ton`, `mile`, `km`, `MCF`, `MMBtu`, `CCF`, `USD`

### Step 3: Calculate

Run the full inventory calculation using Python for detailed output:

```bash
cd ~/ghg-calculator && uv run python -c "
import json
from ghg_calculator.engine.calculator import GHGCalculator
from ghg_calculator.models.activity import ActivityRecord

with open('<scenario_slug>.json') as f:
    data = json.load(f)

activities = [ActivityRecord(**r) for r in data]
calc = GHGCalculator()
inv = calc.calculate_inventory(activities, name='<Title>', year=<year>)

print(f'TOTAL: {inv.total_co2e_tonnes:,.0f} tCO2e ({inv.total_co2e_tonnes/1e6:.2f} MtCO2e)')
print(f'  Scope 1: {inv.scope1.total_co2e_tonnes:,.0f} tCO2e')
print(f'  Scope 2 (Location): {inv.scope2_location.total_co2e_tonnes:,.0f} tCO2e')
print(f'  Scope 3: {inv.scope3.total_co2e_tonnes:,.0f} tCO2e')
for r in inv.all_results:
    if r.scope2_method and r.scope2_method.value == 'market_based':
        continue
    print(f'    {(r.activity_name or r.activity_id or \"\")[:55]:55s} {r.total_co2e_tonnes:>10,.0f} tCO2e')
"
```

### Step 4: Generate Report

```bash
cd ~/ghg-calculator && uv run ghg report <scenario_slug>.json --output <scenario_slug>_report.html --title "<Report Title>"
```

Then open it: `open <scenario_slug>_report.html`

### Step 5: Summarize

Present results to the user with:
- Total emissions in tCO2e and MtCO2e
- Scope breakdown table
- Top 5 emission sources
- Context comparisons (e.g., "equivalent to X passenger cars" at 4.6 tCO2e/car/year)
- Caveats about assumptions made
- Sources used for activity data

## Available Emission Factor Databases (967 factors)

| Source | Factors | Coverage |
|--------|---------|----------|
| EPA Hub | 113 | US stationary/mobile combustion, refrigerants |
| eGRID | 122 | US electricity grid subregions (27 regions + variants) |
| DEFRA | 117 | UK/intl transport, materials, waste, hotels |
| USEEIO | 264 | US spend-based by NAICS sector (kg CO2e/USD) |
| Ember | 120 | International electricity (120 countries) |
| EXIOBASE | 231 | Multi-regional IO (EU, CN, JP, IN, BR, RU, ROW) |

## eGRID Subregion Codes (US)

AKGD, AKMS, AZNM, CAMX, ERCT (Texas), FRCC, HIMS, HIOA, MROE, MROW, NEWE, NWPP, NYCW, NYLI, NYUP, PRMS, RFCE, RFCM, RFCW, RMPA, SPNO, SPSO, SRMV, SRMW, SRSO, SRTV, SRVC

## Reference Emission Factors

- Natural gas: 5.3 kg CO2e/therm
- Diesel: 10.21 kg CO2/gallon
- Gasoline: 8.78 kg CO2/gallon
- US grid average: 0.37 kg CO2/kWh
- ERCOT (Texas): 0.37 kg CO2/kWh
- CAMX (California): 0.24 kg CO2/kWh
- Passenger car: ~4.6 tCO2e/year
