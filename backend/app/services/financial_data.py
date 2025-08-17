import requests

BASE_URL = "https://api-indian-financial-markets-485071544262.asia-south1.run.app/"

# 1. Get all historical financial data for a company
def get_company_data(company_id: str):
    url = f"{BASE_URL}/companies/{company_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 2. Get all historical financial data for a company based on statement
def get_company_data_from_financials(company_id: str, statement_name: str):
    url = f"{BASE_URL}/companies/{company_id}/financials/{statement_name}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 3. Get a specific financial parameter from a company's statement
def get_company_data_from_financial_parameter(company_id: str, statement_name: str, parameter: str):
    url = f"{BASE_URL}/companies/{company_id}/financials/{statement_name}/{parameter}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 4. Get all companies in a sector
def get_companies_in_sector(sector: str):
    url = f"{BASE_URL}/sectors/{sector}/companies/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 5. Get financial data for all companies in a sector
def get_financials_in_sector(sector: str):
    url = f"{BASE_URL}/sectors/{sector}/financials/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 6. Get all conference call transcripts for a company
def get_all_company_conference_calls(company_id: str):
    url = f"{BASE_URL}/companies/{company_id}/conferencecall/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 7. Get conference call transcripts for a time period
def get_company_conference_call_period(company_id: str, time_period: str):
    url = f"{BASE_URL}/companies/{company_id}/conferencecall/{time_period}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 8. Search for top-k similar text chunks
def search_chunks(query: str, k: int, company_name: str, statement_type: str, time_period: str):
    url = f"{BASE_URL}/chunks/search"
    payload = {
        "query": query,
        "k": k,
        "company_name": company_name,
        "statement_type": statement_type,
        "time_period": time_period
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

# ---------------- New Conference Call Endpoints (Latest API) ---------------- #

def get_companies_with_conference_calls():
    """GET /companies/conference-calls/"""
    url = f"{BASE_URL}/companies/conference-calls/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_conference_call_details(company_id: int):
    """GET /companies/{company_id}/conference-calls/details/"""
    url = f"{BASE_URL}/companies/{company_id}/conference-calls/details/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_conference_call_summary(company_id: int, fiscal_year: int, fiscal_quarter: int):
    """GET /companies/{company_id}/conference-calls/{fiscal_year}/{fiscal_quarter}/summary/"""
    url = f"{BASE_URL}/companies/{company_id}/conference-calls/{fiscal_year}/{fiscal_quarter}/summary/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def conference_call_qa(company_id: int, fiscal_year: int, fiscal_quarter: int, question: str, k: int = 3):
    """POST /companies/{company_id}/conference-calls/{fiscal_year}/{fiscal_quarter}/qa/"""
    url = f"{BASE_URL}/companies/{company_id}/conference-calls/{fiscal_year}/{fiscal_quarter}/qa/"
    payload = {"question": question, "k": k}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()