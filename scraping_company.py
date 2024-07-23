import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor

def getCompanyInfo(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Get company address
        address_div = soup.find('div', class_='text-decoration-underline')
        address = address_div.text.strip() if address_div else "N/A"
        
        # Get company contact info
        contact_info = soup.find_all('a', class_='text-decoration-underline')
        phone = contact_info[0].text.strip() if len(contact_info) > 0 else "N/A"
        email = contact_info[1].text.strip() if len(contact_info) > 1 else "N/A"
        website = contact_info[2]['href'] if len(contact_info) > 2 else "N/A"
        print(url)
        return address, phone, email, website
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        print(f"Error parsing company info: {e}")
        return "N/A", "N/A", "N/A", "N/A"

def fetchCompanyData(row):
    try:
        first_td = row.find("td")
        if first_td:
            a_tag = first_td.find("a")
            if a_tag and 'href' in a_tag.attrs:
                company_name = a_tag.text.strip()
                href = a_tag['href']
                address, phone, email, website = getCompanyInfo("https://hibid.com" + href)
                return [company_name, address, phone, email, website]
    except Exception as e:
        print(f"Error fetching company data: {e}")
    return None

def main():
    company_data = []
    # URL of the company search page
    for page in range(1, 33):
        url = 'https://hibid.com/companysearch?apage=' + str(page)
        try:
            r = requests.get(url)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Finding all <tr> elements with the class 'ng-star-inserted'
            rows = soup.find_all('tr', class_='ng-star-inserted')
            
            # List to store company data
            

            # Use ThreadPoolExecutor to fetch data in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(fetchCompanyData, rows)
                
            for result in results:
                if result:
                    company_data.append(result)
            
           
        except requests.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Error in main function: {e}")
     # Write the data to a CSV file
    with open('company_info.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Address", "Phone", "Email", "Website"])
        writer.writerows(company_data)
if __name__ == "__main__":
    main()
