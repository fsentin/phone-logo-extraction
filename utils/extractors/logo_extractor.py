import sys
from .base_extractor import BaseExtractor
from urllib.parse import urljoin, urlparse
import os
from fuzzywuzzy import fuzz
import tldextract

class LogoExtractor(BaseExtractor):
    """
    Extractor to find logos from webpages.
    """

    def extract(self, soup, base_url):
    
        images = soup.find_all('img')

        if images.__len__() == 0:
            sys.stderr.write("Error: no images found in the webpage")
            return None

         # Extract domain name from base URL using tldextract
        parsed_base_url = urlparse(base_url)
        extracted = tldextract.extract(parsed_base_url.netloc)

        print(extracted)

        # Ensure we extract only the second-level domain (SLD)
        domain_name = extracted.domain.lower()
        
        print(domain_name)

        candidates = []
        for image in images:
            if image.has_attr('src'):
                src = image['src']
                
                # Handle protocol-relative URLs
                if src.startswith('//'):
                # Add the protocol from the base URL
                    src = f"{parsed_base_url.scheme}:{src}"
                elif src.startswith('/'):
                    # Convert relative URL to absolute
                    src = urljoin(base_url, src)
                elif not src.startswith('http'):
                    # Handle relative paths without leading slash
                    src = urljoin(base_url, src)
                
                image_name = os.path.basename(src).lower()
                print(image_name)

                score = self.score_image_name(image_name, domain_name)
                candidates.append((src, score))
        
        print(candidates)
        
        if candidates.__len__ == 0:
            sys.stderr.write("Error: no logos found in the webpage")
            return None
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[0][0]
    

    def score_image_name(self, image_name, domain_name, domain_importance=110, logo_importance=105):
        """
        Scores the image name based on the domain and logo importance, with a fallback to fuzzy matching, if no match is found.
        """
        domain_match = domain_importance if domain_name in image_name else 0
        logo_match = logo_importance if "logo" in image_name else 0 

        score = domain_match + logo_match
        
        if not score:
            score = fuzz.partial_ratio(domain_name.lower(), image_name)

        return score
