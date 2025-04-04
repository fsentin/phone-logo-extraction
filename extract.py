import sys
from utils.html_parser import fetch_and_parse_html
from utils.extractors import PhoneExtractor, LogoExtractor

def main(url):
    
    soup, base_url = fetch_and_parse_html(url)

    if soup is None or base_url is None:
        sys.exit(1)
        
    extractors = [
        PhoneExtractor(),
        LogoExtractor(),
    ]
        
    results = []
    for extractor in extractors:
        result = extractor.extract(soup, base_url)
        if result:
            if isinstance(result, list):
                results.append(', '.join(result))
            else:
                results.append(result)
        else:
            results.append('None')
        
    for result in results:
        print(result)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f"Error: Invalid argument input\nExpected input format: python extract.py <input_url>\n")
        sys.exit(1)
    
    main(sys.argv[1])
