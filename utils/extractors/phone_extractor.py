from .base_extractor import BaseExtractor

class PhoneExtractor(BaseExtractor):
    """
    Extractor to find phone numbers from webpages.
    """

    def extract(self, soup, base_url):
        print("Phone Number")
        return