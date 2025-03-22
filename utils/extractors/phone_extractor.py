from .base_extractor import BaseExtractor
import re
import phonenumbers 

class PhoneExtractor(BaseExtractor):
    """
    Extractor to find phone numbers from webpages.
    """

    def extract(self, soup, base_url):

        # Extract phone numbers from tel: links
        tel_links = soup.find_all('a', href=True)
        phone_numbers_from_links = [self.clean_phone_number(link['href'][4:]) for link in tel_links if link['href'].startswith('tel:')]

        # Extract phone numbers using regular expressions
        text = soup.get_text()
        #phone_numbers_from_text = self.extract_phone_numbers_from_text(text)

        # Extract phone numbers using phonenumbers library
        phone_numbers_from_phonenumbers = self.extract_phone_numbers_using_phonenumbers(text)

        phone_numbers_from_span = self.extract_phone_number_from_span(soup)

        # Combine all extracted phone numbers
        phone_numbers = phone_numbers_from_links + phone_numbers_from_phonenumbers + phone_numbers_from_span#+ phone_numbers_from_text 


        # Remove duplicates and empty strings
        phone_numbers = list(set([num for num in phone_numbers if num]))

        if phone_numbers:
            print(phone_numbers)
            return phone_numbers
        else:
            return None

    def clean_phone_number(self, phone_number):
        # Remove any character that is not a number, plus sign, or parenthesis
        return re.sub(r'[^0-9+\(\)]', ' ', phone_number)

    def extract_phone_numbers_from_text(self, text):
        # Regular expression pattern to match common phone number formats
        pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\+\d{1,2}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\(\d{3}\)[-.]?\d{3}[-.]?\d{4}\b'
        return re.findall(pattern, text)

    
    def extract_phone_numbers_using_phonenumbers(self, text):
        matches = phonenumbers.PhoneNumberMatcher(text, None)
        phone_numbers = []
        for match in matches:
            number = match.number
            formatted_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
            phone_numbers.append(formatted_number)
        return phone_numbers
    
    def extract_phone_number_from_span(self, soup):
        # Find all span elements with itemprop="telephone"
        phone_spans = soup.find_all('span', {'itemprop': 'telephone'})
        print(f"Found spans: {[span.get_text(strip=True) for span in phone_spans]}")
        
        phone_numbers = []
        
        for span in phone_spans:
            phone_text = span.get_text(strip=True)
            cleaned_number = self.clean_phone_number(phone_text)
            if cleaned_number:
                phone_numbers.append(cleaned_number)

        return phone_numbers

