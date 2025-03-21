import sys
from .base_extractor import BaseExtractor
from urllib.parse import urljoin, urlparse
import os
from fuzzywuzzy import fuzz
import tldextract
import base64
from io import BytesIO
from PIL import Image

class LogoExtractor(BaseExtractor):
    """
    Extractor to find logos from webpages.
    """

    def extract(self, soup, base_url):

        images = soup.find_all('img')

        if images.__len__() == 0:
            sys.stderr.write("Error: no images found in the webpage")
            return None
    
        domain_name = self.extract_domain(base_url)
        print(domain_name)

        candidates = []
        for image in images:
            if not image.has_attr('src'):
                continue
            src = image['src']

            if src.startswith('data:image/'):
                try:
                    base64_data = src.split(',')[1]
                    decoded_bytes = base64.b64decode(base64_data)
                    image_bytes = BytesIO(decoded_bytes)
                    img = Image.open(image_bytes)
                    image_name = 'base64_image'
                except:
                    sys.stderr.write(f"Error: processing base64 image: {src}\n")
                    continue
            else:
                src = self.resolve_image_url(src, base_url)
                
            image_name = os.path.basename(src).lower() if src != 'base64_image' else 'base64_image'
            alt_text = image.get('alt', '').lower()

            print(image_name)
            print(alt_text)

            score = self.score_image_name(image_name, alt_text, domain_name)
            candidates.append((src, score))
        
        print(candidates)
        
        if len(candidates) == 0:
            sys.stderr.write("Error: no logos found in the webpage")
            return None
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[0][0]
    

    def score_image_name(self, image_name, alt_text, domain_name, domain_importance=110, logo_importance=105):
        """
        Scores the image name based on the domain and logo importance, with a fallback to fuzzy matching, if no match is found.
        """
        score = 0
        if domain_name in image_name:
            score += domain_importance
        if domain_name in alt_text:
            score += domain_importance

        if "logo" in image_name:
            score += logo_importance
        if "logo" in alt_text:
            score += logo_importance
        
        if score == 0:
            score = fuzz.partial_ratio(domain_name.lower(), image_name)

        return score
    
    def extract_domain(self, base_url):
        """
        Extract the domain name from the base URL using tldextract.
        """
        parsed_base_url = urlparse(base_url)
        extracted = tldextract.extract(parsed_base_url.netloc)
        return extracted.domain.lower()
    
    def resolve_image_url(self, src, base_url):
        """
        Resolves relative image URLs to absolute URLs.
        """
        # Handle protocol-relative URLs
        if src.startswith('//'):
            src = f"{urlparse(base_url).scheme}:{src}"
        elif src.startswith('/') or not src.startswith('http'):
            # Convert relative URL to absolute
            src = urljoin(base_url, src)
        return src
