# GHG Emissions Calculator

A production-grade GHG Protocol Corporate Standard emissions calculator with **967 embedded emission factors**, a CLI (`ghg`), an MCP server (`ghg-mcp`), and a Claude Code skill (`/ghg-analyze`).

## Quick Start

```bash
# Install
git clone https://github.com/starrybodies/ghg-calculator.git
cd ghg-calculator
uv sync

# Calculate emissions
uv run ghg calculate --scope 1 --category stationary_combustion \
  --fuel natural_gas --quantity 1000 --unit therm
# → 5,307 kg CO2e (5.3 tCO2e)

# Search emission factors
uv run ghg factors "natural gas"

# Generate a report
uv run ghg report sample.json --output report.html
open report.html
```

## Claude Code Skill

Install the `/ghg-analyze` skill to calculate emissions for any scenario directly from Claude Code:

```bash
# Copy skill to your global Claude skills directory
cp -r .claude/skills/ghg-analyze ~/.claude/skills/
```

Then use it from any project:

```
/ghg-analyze hyperscaler data center buildout in Texas 2025
/ghg-analyze my company's 200-truck diesel fleet in Ohio
/ghg-analyze Bitcoin mining operation 50MW in Iceland
```

The skill researches real-world data, builds activity records, runs calculations across all scopes, and generates interactive HTML reports.

## Features

- **All 3 Scopes** — Scope 1 (direct), Scope 2 (dual location + market-based), Scope 3 (all 15 categories)
- **967 Emission Factors** from 6 free databases:
  - EPA Hub (US combustion + refrigerants)
  - eGRID (US electricity grid, 27 subregions)
  - DEFRA (UK/intl transport, materials, waste)
  - USEEIO (US spend-based by NAICS sector)
  - Ember (international electricity, 120 countries)
  - EXIOBASE (multi-regional input-output)
- **Per-gas breakdown** — CO2, CH4, N2O calculated separately, converted via GWP (AR5/AR6)
- **Unit conversion** — pint-based, handles therms, CCF, MCF, MMBtu, short tons, and more
- **CLI** — `ghg calculate`, `ghg factors`, `ghg gwp`, `ghg convert`, `ghg validate`, `ghg report`
- **MCP Server** — 8 tools for AI agent integration
- **HTML Reports** — interactive Plotly charts (donut, bar, waterfall, treemap)
- **92 tests** — unit, integration, and end-to-end

## CLI Commands

```bash
ghg calculate   # Calculate emissions for a single activity
ghg factors     # Search the emission factor database
ghg gwp         # Look up Global Warming Potential values
ghg convert     # Convert between units
ghg validate    # Validate a JSON activity file
ghg report      # Generate HTML report from activity data
```

## MCP Server

```bash
uv run ghg-mcp  # Start the MCP server
```

Tools: `calculate_emissions`, `calculate_single`, `get_emission_factors`, `list_scopes`, `list_factor_sources`, `generate_report`, `get_gwp_values`, `convert_units`

## Activity Record Format

```json
{
  "scope": "scope_1",
  "scope1_category": "stationary_combustion",
  "fuel_type": "natural_gas",
  "quantity": 1000,
  "unit": "therm"
}
```

See `sample.json` for a complete multi-scope example.

## License

MIT
