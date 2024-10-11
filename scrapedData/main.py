import requests
from bs4 import BeautifulSoup
import csv
import time  # Import time for adding delay between requests

# Base URL of the website with pagination
base_url = 'https://dmp.sante.gov.ma/basesdedonnes/societes-de-dispositifs-medicaux'

# Function to scrape a single page and return its data
def scrape_page(page_number):
    # Construct the URL for the current page
    url = f"{base_url}?page={page_number}&search="
    
    # Send HTTP GET request (disable SSL verification for now)
    response = requests.get(url, verify=False)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table on the page
    table = soup.find('table')
    if not table:
        print(f"No table found on page {page_number}.")
        return None

    # Extract headers from the thead (only once, if it's the first page)
    if page_number == 1:
        thead = table.find('thead')
        headers = [cell.get_text(strip=True) for cell in thead.find_all('th')]
    else:
        headers = None

    # Extract rows from tbody
    tbody = table.find('tbody')
    rows = []
    if tbody:
        for row in tbody.find_all('tr'):
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            rows.append(row_data)

    return headers, rows

# Main function to scrape all pages and write to CSV
def scrape_all_pages():
    last_page = 15
    # Set the last page to stop at
    headers_written = False
    
    with open('listeDesDispositifsMedicaux.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for page_number in range(1, last_page + 1):
            try:
                # Scrape the current page
                result = scrape_page(page_number)
                
                if result is None:
                    print(f"Skipping page {page_number} due to failure.")
                    continue  # Skip this page if it failed

                headers, rows = result

                # Write headers only for the first page
                if not headers_written and headers:
                    writer.writerow(headers)
                    headers_written = True

                # Write the rows to the CSV file
                writer.writerows(rows)

                print(f"Page {page_number} scraped successfully.")
                
                # Optional: Add a delay to avoid overwhelming the server
                time.sleep(1)

            except Exception as e:
                print(f"An error occurred on page {page_number}: {e}")
                continue  # Skip this page if any other exception occurs

    print("All pages scraped and data saved to 'listeDesPharmacies.csv'.")

# Run the script
scrape_all_pages()
