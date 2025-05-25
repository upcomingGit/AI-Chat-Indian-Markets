def get_historical_financials(sector: str, years: int):
    # Mock data — replace with your DB/API call
    return {
        "sector": sector,
        "years": years,
        "trend": [
            {"year": 2023, "revenue": 120},
            {"year": 2022, "revenue": 100},
            {"year": 2021, "revenue": 95}
        ]
    }
