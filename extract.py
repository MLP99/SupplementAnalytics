import requests
from bs4 import BeautifulSoup
import pandas as pd
import dataclasses
from datetime import datetime
pd.set_option('display.max_colwidth', None)


def extract_data(url: str) -> pd.DataFrame:
    """
    Extracts data from the Jumbo website to scape chicken data.

    Parameters:
    a (string): The url that needs to be scraped.

    Returns:
    Pandas DataFrame: a DataFrame that contains the data.
    """
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        results = requests.get(url, headers=headers)
        results.raise_for_status()  # Raise an exception if there was an HTTP error
        soup = BeautifulSoup(results.content, "html.parser")

    except requests.exceptions.RequestException as e:
        # Handle any requests exceptions (e.g. connection error, timeout)
        print(f"Error making request to {url}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there was an error

    try:
        title = soup.find('h1', class_='jum-heading h3').text.strip()
    except AttributeError:
        title = None
    try:
        price = soup.find('div', class_='current-price').text.strip()
    except AttributeError:
        price = None
    try:
        weight = soup.find('h2', class_='jum-heading product-subtitle h6').text.strip()
    except AttributeError:
        weight = None
    try:
        price_per_unit = soup.find('div', class_='price-per-unit').text.strip()
    except AttributeError:
        price_per_unit = None
    try:
        image_url = soup.find('img').attrs['src']
    except AttributeError:
        image_url = None

    df = pd.DataFrame(
            {'title': title,
             'price': price,
             'weight': weight,
             'supermarket': 'Jumbo',
             'price_per_unit per unit': price_per_unit,
             'image_url': image_url,
             'date': datetime.now()
            }, index=[0])
   
    try:
        macro = pd.DataFrame(
        (e.stripped_strings for e in soup.select('table tr:not(:has(th,td.sub-label,td[colspan]))')),
        ).set_index(0).T
        macro.columns = ['energy', 'fats', 'carbs', 'fibers', 'protein','salt']
    except AttributeError:
        macro = None

    df.reset_index(drop=True, inplace=True)
    
    if macro is not None:
        macro.reset_index(drop=True, inplace=True)
        df_concat = pd.concat([df, macro], axis=1)
    else:
        df_concat = df

    print(df_concat)
    print(df_concat['date'])

    return df_concat


def main():
    jumbo_chicken = extract_data('https://www.jumbo.com/producten/jumbo-scharrelkip-filet-800g-515026BAK')
    jumbo_chicken.to_csv('data/jumbo_chicken.csv', index=False)

if __name__ == "__main__":
    main()
