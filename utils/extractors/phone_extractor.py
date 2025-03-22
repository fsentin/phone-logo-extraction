from .base_extractor import BaseExtractor
import re
import sys
import phonenumbers

class PhoneExtractor(BaseExtractor):
    """
    Extractor to find phone numbers from webpages.
    """

    def extract(self, soup, base_url):
        """
        Extract phone numbers from a BeautifulSoup parsed webpage
        
        Args:   
            soup: BeautifulSoup object of the parsed webpage
            base_url: Base URL of the webpage
        
        Returns:
            List of phone numbers found in the webpage or None if no phone numbers found
        """

        # from tel: links
        tel_links = soup.find_all('a', href=True)
        phone_numbers_from_links = [self._clean_phone_number(link['href'][4:]) for link in tel_links if link['href'].startswith('tel:')]

        text = soup.get_text()
        phone_numbers_from_text = self._extract_phone_numbers_from_text(text)
        phone_numbers_from_phonenumbers = self._extract_phone_numbers_using_phonenumbers(text)
        phone_numbers_from_span = self._extract_phone_number_from_span(soup)
        phone_numbers_from_elements = self._extract_from_common_elements(soup)

        # combine all 
        phone_numbers = (
            phone_numbers_from_links + 
            phone_numbers_from_text + 
            phone_numbers_from_phonenumbers + 
            phone_numbers_from_span +
            phone_numbers_from_elements
        )

        # remove duplicates
        normalized_numbers = self._normalize_phone_numbers(phone_numbers)

        if normalized_numbers:
            return normalized_numbers
        else:
            return None

    def _clean_phone_number(self, phone_number):
        """
        Clean phone number by removing any characters that are not numbers, plus signs, or parentheses
            
        Args:
            phone_number: Phone number to clean
        
        Returns:    
            Cleaned phone number
        """
        if not phone_number:
            return ""
        
        cleaned = re.sub(r'[^0-9+\(\)\- ]', '', phone_number).strip()
        return re.sub(r'-', ' ', cleaned)
        
    

    def _extract_phone_numbers_from_text(self, text):
        
        if not text:
            return []
            
        patterns = [
            # international format +1 123-456-7890
            r'\+\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{4}',
            # US format (123) 456-7890
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
            # US format 123-456-7890
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            # 10-digit number 1234567890
            r'\b\d{10}\b',
            # Format with dots 123.456.7890
            r'\b\d{3}\.\d{3}\.\d{4}\b',
            # Format with spaces 123 456 7890
            r'\b\d{3}\s\d{3}\s\d{4}\b'
        ]
        
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            results.extend(matches)
            
        return results

    def _extract_phone_numbers_using_phonenumbers(self, text):
       
        if not text:
            return []
            
        try:
            matches = phonenumbers.PhoneNumberMatcher(text, None)
            phone_numbers = []
            for match in matches:
                number = match.number
                phone_numbers.append(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164))
            return phone_numbers
        except Exception as e:
            sys.stderr.write(f"Error in phonenumbers extraction: {e}")
            return []
    
    def _extract_phone_number_from_span(self, soup):
       
        if not soup:
            return []
            
        # spans with telephone attributes
        phone_spans = soup.find_all(['span', 'div', 'p'], {
            'itemprop': ['telephone', 'phone', 'faxNumber']
        })
        
        # class and id containing 'phone' or 'tel'
        phone_spans += soup.find_all(
            lambda tag: any(attr in (tag.get('class', []) + [tag.get('id', '')]) 
                           for attr in ['phone', 'tel', 'fax'])
        )
        
        phone_numbers = []
        
        for span in phone_spans:
            phone_text = span.get_text(strip=True)
            cleaned_number = self.clean_phone_number(phone_text)
            if cleaned_number:
                phone_numbers.append(cleaned_number)

        return phone_numbers
        
    def _extract_from_common_elements(self, soup):
       
        if not soup:
            return []
            
        potential_elements = []
        
        potential_elements.extend(soup.find_all(attrs={"itemtype": "http://schema.org/Organization"}))
        potential_elements.extend(soup.find_all(attrs={"itemtype": "http://schema.org/Person"}))
        potential_elements.extend(soup.find_all(attrs={"itemtype": "http://schema.org/LocalBusiness"}))
        
        potential_elements.extend(soup.find_all(class_=lambda c: c and any(
            term in c for term in ["contact", "footer", "header", "phone", "tel"]
        )))
        
        phone_numbers = []
        for element in potential_elements:
            text = element.get_text()
            phone_numbers.extend(self._extract_phone_numbers_from_text(text))
            
        return phone_numbers
        
    def _normalize_phone_numbers(self, phone_numbers):

        if not phone_numbers:
            return []
            
        # filter out empty strings, normalize whitespace
        cleaned_numbers = [re.sub(r'\s+', ' ', num).strip() for num in phone_numbers if num]
        
        # remove all non-numeric characters 
        normalized_map = {}
        for number in cleaned_numbers:
            # deduplication
            digits_only = re.sub(r'\D', '', number)
            if digits_only:
                normalized_map[digits_only] = self._clean_phone_number(number)
        
        return list(normalized_map.values())