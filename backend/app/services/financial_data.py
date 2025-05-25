import requests

# 1. Get performance of all companies in a specific sector
def get_sector_performance(sector: str):
    url = f"https://api-indian-markets.azurewebsites.net/sectors/{sector}/financials/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 2. Get performance of a specific company
def get_company_performance(company: str):
    url = f"https://api-indian-markets.azurewebsites.net/companies/{company}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 3. Get all the companies in a sector
def get_companies_in_sector(sector: str):
    url = f"https://api-indian-markets.azurewebsites.net/sectors/{sector}/companies/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 4. Get trends of a specific financial statement for a specific company
def get_company_statement_trends(company: str, statement: str):
    url = f"https://api-indian-markets.azurewebsites.net/companies/{company}/financials/{statement}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()