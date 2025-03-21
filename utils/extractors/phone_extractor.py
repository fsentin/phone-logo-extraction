from .base_extractor import BaseExtractor
import re
from phonenumbers import PhoneNumberMatcher

class PhoneExtractor(BaseExtractor):
    """
    Extractor to find phone numbers from webpages.
    """

    def extract(self, soup, base_url):
        print("Phone Number")

        tel_links = soup.find_all('a', href=True)

        phone_numbers = [self.clean_phone_number(link['href'][4:]) for link in tel_links if link['href'].startswith('tel:')]

        if phone_numbers:
            print(phone_numbers)
            return phone_numbers
        else:
            return None
        
    def clean_phone_number(self, phone_number):
    # Remove any character that is not a number, plus sign, or parenthesis
        return re.sub(r'[^0-9+\(\)]', ' ', phone_number)