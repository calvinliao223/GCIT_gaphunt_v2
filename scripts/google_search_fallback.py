#!/usr/bin/env python3
"""
Google Custom Search API fallback for research paper search
More reliable for cloud deployments
"""

import os
import requests
import time
from typing import List, Dict

class GoogleScholarFallback:
    """Fallback Google Scholar search using Custom Search API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_CSE_ID', '017576662512468239146:omuauf_lfve')  # Default Scholar CSE
        
    def search_papers(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search for academic papers using Google Custom Search API
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of paper dictionaries
        """
        if not self.api_key:
            print("⚠️ Google API key not found")
            return []
            
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            
            headers = {
                'User-Agent': 'Gap-Hunter-Bot/1.0 (Academic Research Tool; contact@gaphunter.com)',
                'Referer': 'https://gcitgaphuntv2-cezcegykumtsirmsaejf3g.streamlit.app/'
            }
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': f'"{query}" filetype:pdf OR site:scholar.google.com OR site:arxiv.org',
                'num': min(num_results, 10),  # Max 10 per request
                'safe': 'off',
                'fields': 'items(title,link,snippet,displayLink)'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data.get('items', []):
                    paper = {
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'abstract': item.get('snippet', ''),
                        'source': item.get('displayLink', ''),
                        'year': self._extract_year(item.get('snippet', '')),
                        'authors': self._extract_authors(item.get('snippet', '')),
                        'journal_name': self._extract_journal(item.get('displayLink', ''))
                    }
                    papers.append(paper)
                
                print(f"✅ Found {len(papers)} papers via Google Custom Search")
                return papers
                
            elif response.status_code == 403:
                print("❌ Google API quota exceeded or access denied")
                return []
            else:
                print(f"⚠️ Google Search API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Google Search error: {e}")
            return []
    
    def _extract_year(self, text: str) -> str:
        """Extract publication year from text"""
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        return year_match.group() if year_match else ''
    
    def _extract_authors(self, text: str) -> str:
        """Extract author names from text"""
        # Simple heuristic - look for patterns like "Author Name, Author Name"
        import re
        author_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:, [A-Z][a-z]+ [A-Z][a-z]+)*)'
        match = re.search(author_pattern, text)
        return match.group() if match else ''
    
    def _extract_journal(self, display_link: str) -> str:
        """Extract journal name from display link"""
        if 'arxiv.org' in display_link:
            return 'arXiv'
        elif 'scholar.google.com' in display_link:
            return 'Google Scholar'
        elif 'ieee.org' in display_link:
            return 'IEEE'
        elif 'acm.org' in display_link:
            return 'ACM'
        elif 'springer.com' in display_link:
            return 'Springer'
        else:
            return display_link.replace('www.', '').split('.')[0].title()

def test_google_fallback():
    """Test the Google fallback search"""
    searcher = GoogleScholarFallback()
    results = searcher.search_papers("machine learning healthcare", 5)
    
    print(f"\n📊 Test Results: {len(results)} papers found")
    for i, paper in enumerate(results, 1):
        print(f"\n{i}. {paper['title'][:80]}...")
        print(f"   Source: {paper['source']}")
        print(f"   Year: {paper['year']}")

if __name__ == "__main__":
    test_google_fallback()
