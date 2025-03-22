import sys
from .base_extractor import BaseExtractor
from urllib.parse import urljoin, urlparse, quote
import os
from fuzzywuzzy import fuzz
import tldextract
import base64
from io import BytesIO
from PIL import Image

class LogoExtractor(BaseExtractor):
    """
    Extractor to find most prominent logo from webpage parsed with BeautifulSoup

    Found logos are scored heuristically and the one with the highest score is returned
    """

    DOMAIN_IMPORTANCE = 110
    LOGO_IMPORTANCE = 105

    def extract(self, soup, base_url):
        """
        Extract the most prominent logo from a BeautifulSoup parsed webpage
        
        Args:
            soup: BeautifulSoup object of the parsed webpage
            base_url: Base URL of the webpage
            
        Returns:
            URL of the most prominent logo or None if no logo found
        """

        if soup is None:
            sys.stderr.write("Error: unable to extract from invalid soup\n")
            sys.exit(1)

        candidates = []
        domain_name = self._extract_domain(base_url)

        # <img> tags for logos
        image_tags = soup.find_all('img')

        if image_tags.__len__() == 0:
            sys.stderr.write("Error: no images found in the webpage")
            return None
        
        for image in image_tags:
            if not image.has_attr('src'):
                continue
            src = image['src']
            alt_text = image.get('alt', '').lower()

            if src.startswith('data:image/'):
                score = self._score_base64_image(src, alt_text, domain_name)
                
            else:
                src = self._resolve_image_url(src, base_url)
                src = quote(src, safe=":/")  # encode spaces and special characters
                image_name = os.path.basename(src).lower() 
                score = self._score_image(image_name, alt_text, domain_name)

            candidates.append((src, score))
        
        
        if not candidates:
            sys.stderr.write("Error: no logos found in the webpage")
            return None
        
        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates[0][0]


    def _score_base64_image(self, src, alt_text, domain_name):
        """
        Score an image based on its base64 data, alt text, and relevance to the domain
        
        """
        score = 0
        try:
            mime_type = src.split(';')[0].replace('data:', '')
            base64_data = src.split(',')[1]
            decoded_bytes = base64.b64decode(base64_data)
            image_bytes = BytesIO(decoded_bytes)
            img = Image.open(image_bytes)
            width, height = img.size

            aspect_ratio = width / height if height > 0 else 0

            if 0.8 <= aspect_ratio <= 1.2:
                score += 30
            
            if mime_type in ['image/png', 'image/svg+xml', 'image/webp']:
                score += 25

            if "logo" in alt_text:
                score += self.LOGO_IMPORTANCE
            if domain_name in alt_text:
                score += self.DOMAIN_IMPORTANCE
        
        except:
            sys.stderr.write(f"Error: processing base64 image: {src}\n")
        
        return score
        

    def _score_image(self, image_name, alt_text, domain_name):
        """
        Score an image based on its filename, alt text, and relevance to the domain
        
        """
        score = 0
        if domain_name in image_name:
            score += self.DOMAIN_IMPORTANCE
        if domain_name in alt_text:
            score += self.DOMAIN_IMPORTANCE

        if "logo" in image_name:
            score += self.LOGO_IMPORTANCE
        if "logo" in alt_text:
            score += self.LOGO_IMPORTANCE
        
        if score == 0:
            score = fuzz.partial_ratio(domain_name.lower(), image_name)

        return score
    
    def _extract_domain(self, base_url):
        parsed_base_url = urlparse(base_url)
        extracted = tldextract.extract(parsed_base_url.netloc)
        return extracted.domain.lower()
    
    
    
    def _resolve_image_url(self, src, base_url):
        """
        Resolve a relative image URL to an absolute URL
        
        """
        if src.startswith('//'):
            src = f"{urlparse(base_url).scheme}:{src}"
        elif src.startswith('/') or not src.startswith('http'):
            src = urljoin(base_url, src)
        return src