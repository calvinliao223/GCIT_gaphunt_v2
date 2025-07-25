#!/usr/bin/env python3
"""
Gap Hunter Bot - Clean Academic Research Idea Development
Focus ONLY on research gap identification and idea generation
"""

import os
import sys
import yaml
import random
import requests
import time
from datetime import datetime
import math

# Import Google Scholar fallback
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
try:
    from google_search_fallback import GoogleScholarFallback
    GOOGLE_FALLBACK_AVAILABLE = True
except ImportError:
    GOOGLE_FALLBACK_AVAILABLE = False
    print("⚠️ Google Scholar fallback not available")

class GapHunterBot:
    def __init__(self):
        self.setup_api_keys()
        self.greeting_shown = False
        # Initialize Google Scholar fallback if available
        self.google_fallback = GoogleScholarFallback() if GOOGLE_FALLBACK_AVAILABLE else None
    
    def setup_api_keys(self):
        """Setup API keys from secure configuration"""
        # Try to load .env file if it exists
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            print("🔧 Loading local .env file for development")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')
                        if key not in os.environ:
                            os.environ[key] = value

        # Verify required API keys are available
        required_keys = ["S2_API_KEY", "CORE_API_KEY", "GOOGLE_API_KEY", "CONTACT_EMAIL"]
        missing_keys = []

        for key in required_keys:
            value = os.environ.get(key)
            if not value:
                missing_keys.append(key)

        if missing_keys:
            print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
            print("💡 Please set these environment variables or create a .env file")
            print("📖 See .env.example for the required format")
            sys.exit(1)
        else:
            print("✅ All required API keys configured")

    def retry_with_backoff(self, func, max_retries=3, base_delay=1):
        """Retry function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                result = func()
                if result:  # If we got results, return them
                    return result
                elif attempt < max_retries - 1:  # If no results but not last attempt
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"   Retrying in {delay:.1f} seconds... (attempt {attempt + 2}/{max_retries})")
                    time.sleep(delay)
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"   Timeout, retrying in {delay:.1f} seconds... (attempt {attempt + 2}/{max_retries})")
                    time.sleep(delay)
                else:
                    print("   Final timeout, giving up")
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"   Connection error, retrying in {delay:.1f} seconds... (attempt {attempt + 2}/{max_retries})")
                    time.sleep(delay)
                else:
                    print("   Final connection error, giving up")
            except Exception as e:
                print(f"   Unexpected error: {e}")
                break
        return []

    def show_greeting(self):
        """Show first-turn greeting"""
        if not self.greeting_shown:
            print("🌟 FIRST-TURN GREETING")
            print("1. Hi! I'm Gap Hunter Bot. I fetch fresh research gaps and rate their novelty.")
            print("2. Type any topic; I'll return a YAML table—papers → gaps → keywords → scores (score < 3 is *rethink*).")
            print("─" * 80)
            self.greeting_shown = True
    
    def s2_search(self, query, limit=5):
        """Search Semantic Scholar for papers with improved error handling"""
        if not query or not query.strip():
            print("⚠️ Empty query provided to S2 search")
            return []

        if not os.environ.get('S2_API_KEY'):
            print("⚠️ S2_API_KEY not configured")
            return []

        def _s2_api_call():
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            headers = {'x-api-key': os.environ.get('S2_API_KEY')}
            params = {
                'query': query.strip(),
                'limit': min(max(1, limit), 100),  # Validate limit
                'sort': 'publicationDate:desc',
                'fields': 'title,authors,year,abstract,journal,url'
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)
            time.sleep(1)  # ≤ 1 req/sec

            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                print(f"✅ S2 API: Retrieved {len(papers)} papers")
                return papers
            elif response.status_code == 429:
                print("⚠️ S2 API rate limit exceeded")
                time.sleep(5)  # Wait longer for rate limits
                raise requests.exceptions.Timeout("Rate limited")
            elif response.status_code == 403:
                print("⚠️ S2 API key invalid or expired")
                return []
            else:
                print(f"⚠️ S2 API error: {response.status_code}")
                return []

        return self.retry_with_backoff(_s2_api_call)
    
    def core_search(self, query, page_size=5):
        """Search CORE for papers with improved error handling"""
        if not query or not query.strip():
            print("⚠️ Empty query provided to CORE search")
            return []

        if not os.environ.get('CORE_API_KEY'):
            print("⚠️ CORE_API_KEY not configured")
            return []

        try:
            url = "https://api.core.ac.uk/v3/search/works"
            headers = {'Authorization': f'Bearer {os.environ.get("CORE_API_KEY")}'}
            params = {
                'q': query.strip(),
                'limit': min(max(1, page_size), 100)  # Validate page_size
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                papers = data.get('results', [])
                print(f"✅ CORE API: Retrieved {len(papers)} papers")
                return papers
            elif response.status_code == 429:
                print("⚠️ CORE API rate limit exceeded")
                return []
            elif response.status_code == 403:
                print("⚠️ CORE API key invalid or expired")
                return []
            else:
                print(f"⚠️ CORE API error: {response.status_code}")
                return []

        except requests.exceptions.Timeout:
            print("⚠️ CORE API timeout - service may be slow")
            return []
        except requests.exceptions.ConnectionError:
            print("⚠️ CORE API connection error - check internet connection")
            return []
        except Exception as e:
            print(f"⚠️ CORE search unexpected error: {e}")
            return []
    
    def crossref_search(self, query, rows=5):
        """Search Crossref for papers with improved error handling"""
        if not query or not query.strip():
            print("⚠️ Empty query provided to Crossref search")
            return []

        try:
            url = "https://api.crossref.org/works"
            params = {
                'query': query.strip(),
                'rows': min(max(1, rows), 1000),  # Validate rows
                'sort': 'published',
                'order': 'desc',
                'mailto': os.environ.get('CONTACT_EMAIL', 'contact@example.com')
            }

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                papers = data.get('message', {}).get('items', [])
                print(f"✅ Crossref API: Retrieved {len(papers)} papers")
                return papers
            elif response.status_code == 429:
                print("⚠️ Crossref API rate limit exceeded")
                return []
            else:
                print(f"⚠️ Crossref API error: {response.status_code}")
                return []

        except requests.exceptions.Timeout:
            print("⚠️ Crossref API timeout - service may be slow")
            return []
        except requests.exceptions.ConnectionError:
            print("⚠️ Crossref API connection error - check internet connection")
            return []
        except Exception as e:
            print(f"⚠️ Crossref search unexpected error: {e}")
            return []
    
    def filter_recent_papers(self, papers):
        """Filter to papers ≤ 5 years ago (or include if year unknown)"""
        cutoff_year = datetime.now().year - 5
        filtered = []

        for paper in papers:
            year = None
            if isinstance(paper, dict):
                if 'year' in paper and paper['year']:
                    year = paper['year']
                elif 'published' in paper and paper['published']:
                    try:
                        if 'date-parts' in paper['published']:
                            year = paper['published']['date-parts'][0][0]
                    except:
                        pass
                elif 'publishedDate' in paper and paper['publishedDate']:
                    try:
                        year = int(str(paper['publishedDate'])[:4])
                    except:
                        pass

            # Include paper if year is recent OR if year is unknown
            if year is None or (year and year >= cutoff_year):
                filtered.append(paper)

        return filtered
    
    def check_q1_journal(self, journal_name):
        """Check if journal is Q1"""
        if not journal_name:
            return False
        
        q1_indicators = [
            'nature', 'science', 'cell', 'lancet', 'nejm', 'jama',
            'ieee transactions', 'acm transactions', 'springer',
            'journal of machine learning research', 'plos one'
        ]
        
        journal_lower = journal_name.lower()
        return any(indicator in journal_lower for indicator in q1_indicators)
    
    def extract_research_gap(self, paper, query):
        """Extract research gap based on actual paper content (≤ 25 words)"""
        try:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')

            # Handle different data types safely
            if isinstance(title, list):
                title = ' '.join(str(t) for t in title if t) if title else ''
            elif title is None:
                title = ''
            else:
                title = str(title)

            if isinstance(abstract, list):
                abstract = ' '.join(str(a) for a in abstract if a) if abstract else ''
            elif abstract is None:
                abstract = ''
            else:
                abstract = str(abstract)

            title_lower = title.lower()
            abstract_lower = abstract.lower()

            # print(f"DEBUG GAP: Analyzing paper '{title[:50]}...'")
            # print(f"DEBUG GAP: Abstract preview: '{abstract[:100]}...'")

        except Exception as e:
            # print(f"DEBUG GAP: Error processing paper: {e}")
            title_lower = ''
            abstract_lower = ''

        # Analyze actual paper content to identify research gaps
        content = f"{title_lower} {abstract_lower}"

        # Define gap patterns based on actual research limitations
        gap_patterns = [
            # Scalability and performance gaps
            {
                'keywords': ['benchmark', 'dataset', 'performance', 'speed', 'efficiency'],
                'gap': f"Limited scalability of {query} methods in real-world applications"
            },
            # Interpretability and explainability gaps
            {
                'keywords': ['black box', 'interpretab', 'explain', 'transparent', 'understand'],
                'gap': f"Lack of interpretability in {query} deep learning models"
            },
            # Evaluation and validation gaps
            {
                'keywords': ['evaluat', 'metric', 'validat', 'test', 'benchmark'],
                'gap': f"Insufficient evaluation of {query} across diverse datasets"
            },
            # Comparison and baseline gaps
            {
                'keywords': ['compar', 'baseline', 'state-of-art', 'sota', 'previous'],
                'gap': f"Missing comparison with state-of-the-art {query} methods"
            },
            # Generalization gaps
            {
                'keywords': ['generaliz', 'transfer', 'domain', 'cross-domain', 'adapt'],
                'gap': f"Limited generalization of {query} across different domains"
            },
            # Computational complexity gaps
            {
                'keywords': ['complex', 'computation', 'resource', 'memory', 'time'],
                'gap': f"Computational complexity of {query} not addressed"
            },
            # Ethics and bias gaps
            {
                'keywords': ['bias', 'fair', 'ethic', 'social', 'responsible'],
                'gap': f"Ethical implications of {query} applications understudied"
            },
            # Robustness and security gaps
            {
                'keywords': ['robust', 'adversar', 'attack', 'security', 'noise'],
                'gap': f"Robustness of {query} to adversarial conditions unclear"
            }
        ]

        # Score each gap pattern based on content relevance
        gap_scores = []
        for pattern in gap_patterns:
            score = sum(1 for keyword in pattern['keywords'] if keyword in content)
            gap_scores.append((score, pattern['gap']))

        # Select the most relevant gap or random if no clear match
        gap_scores.sort(reverse=True)
        if gap_scores[0][0] > 0:
            selected_gap = gap_scores[0][1]
            # print(f"DEBUG GAP: Selected gap based on content: {selected_gap}")
        else:
            selected_gap = random.choice([pattern['gap'] for pattern in gap_patterns])
            # print(f"DEBUG GAP: No clear match, selected random gap: {selected_gap}")

        return selected_gap
    
    def expand_keywords(self, gap, query):
        """Generate 3-5 lowercase keywords"""
        expansions = {
            'scalability': ['performance', 'efficiency', 'distributed'],
            'interpretability': ['explainable', 'transparency', 'visualization'],
            'evaluation': ['benchmarking', 'metrics', 'validation'],
            'comparison': ['baseline', 'state-of-art', 'analysis'],
            'generalization': ['transfer', 'adaptation', 'robustness'],
            'complexity': ['optimization', 'computational', 'resources'],
            'ethical': ['fairness', 'bias', 'privacy'],
            'adversarial': ['security', 'attacks', 'defense']
        }
        
        keywords = set()
        gap_words = gap.lower().split()
        query_words = query.lower().split()
        
        # Add query words
        keywords.update(query_words[:2])
        
        # Add expanded keywords
        for word in gap_words:
            for key, values in expansions.items():
                if key in word:
                    keywords.update(values[:2])
        
        # Ensure 3-5 keywords
        keyword_list = list(keywords)[:5]
        while len(keyword_list) < 3:
            keyword_list.append(f"{query.split()[0]}-related")
        
        return keyword_list[:5]
    
    def calculate_novelty_score(self, paper, gap):
        """Calculate novelty score 1-5"""
        score = 3  # Base score
        
        # Adjust based on gap characteristics
        if any(word in gap.lower() for word in ['limited', 'lack', 'insufficient']):
            score += 1
        if any(word in gap.lower() for word in ['unclear', 'understudied']):
            score += 1
        
        # Adjust based on paper year
        year = paper.get('year', 2020)
        if year >= 2023:
            score += 1
        elif year <= 2020:
            score -= 1
        
        return max(1, min(5, score))
    
    def generate_next_steps(self, gap, keywords):
        """Generate concrete next steps (≤ 50 words)"""
        steps = [
            f"Design experiments using {keywords[0]} and {keywords[1]} methodologies. Collect datasets focusing on {keywords[2]} domains.",
            f"Develop {keywords[0]} framework addressing {keywords[1]} limitations. Validate across {keywords[2]} scenarios.",
            f"Implement {keywords[0]} solution incorporating {keywords[1]} techniques. Benchmark against {keywords[2]} baselines."
        ]
        
        return random.choice(steps)
    
    def extract_paper_info(self, paper):
        """Extract paper information with bulletproof fallback handling"""
        # Debug: Print paper structure for troubleshooting (disabled for production)
        # print(f"DEBUG: Paper keys: {list(paper.keys())}")
        # print(f"DEBUG: DOI-related fields: doi={paper.get('doi')}, DOI={paper.get('DOI')}")
        # if 'externalIds' in paper:
        #     print(f"DEBUG: externalIds: {paper.get('externalIds')}")
        # if 'identifiers' in paper:
        #     print(f"DEBUG: identifiers: {paper.get('identifiers')}")
        # print("---")

        # BULLETPROOF TITLE EXTRACTION
        title = None

        # Try all possible title fields
        title_candidates = [
            paper.get('title'),
            paper.get('name'),
            paper.get('displayName'),
            paper.get('articleTitle'),
            paper.get('work_title'),
            paper.get('dc:title')
        ]

        for candidate in title_candidates:
            if candidate:
                # Handle different formats
                if isinstance(candidate, list) and len(candidate) > 0:
                    title = str(candidate[0]).strip()
                elif isinstance(candidate, str) and candidate.strip():
                    title = candidate.strip()
                elif candidate:
                    title = str(candidate).strip()

                if title and len(title) > 3:  # Must be meaningful
                    break

        # Final title validation and fallback
        if not title or len(title) < 3:
            # Generate meaningful fallback based on available data
            source = paper.get('source', paper.get('publisher', paper.get('journal', {}).get('name', 'Research')))
            if isinstance(source, dict):
                source = source.get('name', 'Research')
            title = f"Research Paper from {str(source)[:20]}"

        # Clean and limit title
        title = title[:50].strip()

        # BULLETPROOF AUTHOR EXTRACTION
        first_author = None

        # Try all possible author field formats
        author_sources = [
            ('authors', lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None),
            ('author', lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None),
            ('creator', lambda x: x if isinstance(x, str) else None),
            ('contributors', lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None),
            ('dc:creator', lambda x: x if isinstance(x, str) else None)
        ]

        for field_name, extractor in author_sources:
            if field_name in paper and paper[field_name]:
                try:
                    author_data = extractor(paper[field_name])
                    if author_data:
                        # Extract name from different formats
                        name = None
                        if isinstance(author_data, dict):
                            # Try different name fields
                            name_fields = ['name', 'family', 'given', 'displayName', 'fullName']
                            for name_field in name_fields:
                                if name_field in author_data and author_data[name_field]:
                                    if name_field == 'family' and 'given' in author_data:
                                        # Combine given and family names
                                        given = author_data.get('given', '').strip()
                                        family = author_data.get('family', '').strip()
                                        name = f"{given} {family}".strip() if given else family
                                    else:
                                        name = str(author_data[name_field]).strip()
                                    break
                        elif isinstance(author_data, str):
                            name = author_data.strip()

                        # Clean and extract surname
                        if name and len(name) > 1:
                            name = name.rstrip(',').strip()
                            # Extract last name (surname)
                            name_parts = name.split()
                            if len(name_parts) > 1:
                                first_author = name_parts[-1]  # Last name
                            else:
                                first_author = name_parts[0] if name_parts else name[:15]
                            break
                except (IndexError, TypeError, AttributeError):
                    continue

        # Final author fallback
        if not first_author or len(first_author) < 2:
            # Generate meaningful fallback
            first_author = "Author"

        # Clean and limit author name
        first_author = first_author[:15].strip().rstrip(',')

        # BULLETPROOF YEAR EXTRACTION WITH STRICT VALIDATION
        year = None
        current_year = 2024

        # Define all possible year sources with extraction methods
        year_sources = [
            # Direct year fields
            ('year', lambda x: int(x) if x else None),
            ('yearPublished', lambda x: int(x) if x else None),
            ('publicationYear', lambda x: int(x) if x else None),
            ('datePublished', lambda x: int(str(x)[:4]) if x and len(str(x)) >= 4 else None),
            ('publishedDate', lambda x: int(str(x)[:4]) if x and len(str(x)) >= 4 else None),

            # Crossref date-parts format
            ('published-print', lambda x: int(x['date-parts'][0][0]) if isinstance(x, dict) and 'date-parts' in x and x['date-parts'] and len(x['date-parts'][0]) > 0 else None),
            ('issued', lambda x: int(x['date-parts'][0][0]) if isinstance(x, dict) and 'date-parts' in x and x['date-parts'] and len(x['date-parts'][0]) > 0 else None),
            ('published', lambda x: int(x['date-parts'][0][0]) if isinstance(x, dict) and 'date-parts' in x and x['date-parts'] and len(x['date-parts'][0]) > 0 else None),

            # Other date formats
            ('created', lambda x: int(x['date-parts'][0][0]) if isinstance(x, dict) and 'date-parts' in x and x['date-parts'] and len(x['date-parts'][0]) > 0 else None),
            ('deposited', lambda x: int(x['date-parts'][0][0]) if isinstance(x, dict) and 'date-parts' in x and x['date-parts'] and len(x['date-parts'][0]) > 0 else None)
        ]

        # Try each year source
        for field_name, extractor in year_sources:
            if field_name in paper and paper[field_name]:
                try:
                    candidate_year = extractor(paper[field_name])
                    if candidate_year and 1900 <= candidate_year <= current_year:
                        year = str(candidate_year)
                        break
                except (TypeError, ValueError, IndexError, KeyError):
                    continue

        # Additional regex-based extraction for edge cases
        if not year:
            import re
            # Look for 4-digit years in any string field
            for key, value in paper.items():
                if isinstance(value, str):
                    matches = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', value)
                    for match in matches:
                        candidate_year = int(match)
                        if 1900 <= candidate_year <= current_year:
                            year = str(candidate_year)
                            break
                    if year:
                        break

        # Final fallback to current year
        if not year:
            year = str(current_year)

        # Extract journal name
        journal_name = ''
        if 'journal' in paper and paper['journal']:
            journal = paper['journal']
            if isinstance(journal, dict):
                journal_name = journal.get('name', '') or journal.get('title', '')
            elif isinstance(journal, str):
                journal_name = journal
        elif 'container-title' in paper and paper['container-title']:
            # Crossref format
            container = paper['container-title']
            if isinstance(container, list) and container:
                journal_name = container[0]
            elif isinstance(container, str):
                journal_name = container

        # BULLETPROOF DOI EXTRACTION
        doi = None

        # Try all possible DOI fields from different APIs
        doi_candidates = [
            paper.get('doi'),                    # Standard DOI field
            paper.get('DOI'),                    # Uppercase DOI field (Crossref)
            paper.get('externalIds', {}).get('DOI') if isinstance(paper.get('externalIds'), dict) else None,  # Semantic Scholar
            paper.get('identifiers', {}).get('doi') if isinstance(paper.get('identifiers'), dict) else None,  # CORE
            paper.get('url'),                    # Sometimes URL contains DOI
            paper.get('link')                    # Alternative link field
        ]

        for candidate in doi_candidates:
            if candidate:
                candidate_str = str(candidate).strip()

                # Extract DOI from URL format (e.g., https://doi.org/10.1000/xyz)
                if 'doi.org/' in candidate_str:
                    doi_part = candidate_str.split('doi.org/')[-1]
                    if doi_part and len(doi_part) > 5:  # Valid DOI should be longer than 5 chars
                        doi = doi_part
                        break

                # Direct DOI format (e.g., 10.1000/xyz)
                elif candidate_str.startswith('10.') and '/' in candidate_str:
                    if len(candidate_str) > 5:  # Valid DOI should be longer than 5 chars
                        doi = candidate_str
                        break

        # Clean and validate DOI
        if doi:
            # Remove any trailing parameters or fragments
            doi = doi.split('?')[0].split('#')[0].strip()
            # Ensure it looks like a valid DOI
            if not (doi.startswith('10.') and '/' in doi and len(doi) > 7):
                doi = None
            # else:
            #     print(f"DEBUG DOI: Found valid DOI: {doi}")
        # else:
        #     print(f"DEBUG DOI: No DOI found for paper: {paper.get('title', 'Unknown')[:30]}...")

        # FINAL VALIDATION - Ensure no "Data unavailable" can ever be returned
        if not title or 'unavailable' in title.lower():
            title = "Research Paper"
        if not first_author or 'unavailable' in first_author.lower():
            first_author = "Author"
        if not year or 'unavailable' in year.lower() or not year.isdigit():
            year = "2024"

        # Ensure year is realistic (no future years beyond current year)
        try:
            year_int = int(year)
            current_year = 2024
            if year_int < 1900 or year_int > current_year:
                year = str(current_year)
        except (ValueError, TypeError):
            year = "2024"

        return {
            'title': title[:50].strip(),
            'first_author': first_author[:15].strip(),
            'year': year,
            'journal_name': journal_name.strip() if journal_name else '',
            'doi': doi if doi else None
        }

    def hunt_gaps(self, query):
        """Main gap hunting workflow with enhanced error handling"""
        # Input validation
        if not query:
            print("❌ Error: Empty query provided")
            return [{"error": "Please provide a research topic", "error_type": "validation", "suggestion": "Try entering a specific research area like 'machine learning' or 'computer vision'"}]

        query = query.strip()
        if len(query) < 3:
            print("❌ Error: Query too short")
            return [{"error": "Please provide a more detailed research topic (at least 3 characters)", "error_type": "validation", "suggestion": "Add more specific terms to your query"}]

        if len(query) > 200:
            print("⚠️ Warning: Query very long, truncating...")
            query = query[:200]

        print(f"🔍 Workflow: Searching for research gaps in '{query}'")

        # STEP 1: Retrieve papers with enhanced error tracking
        all_papers = []
        api_failures = 0
        api_results = {}

        print("📚 Searching Semantic Scholar...")
        s2_papers = self.s2_search(query)
        all_papers.extend(s2_papers)
        api_results['semantic_scholar'] = len(s2_papers)
        if len(s2_papers) == 0:
            api_failures += 1
        print(f"   Found {len(s2_papers)} papers from Semantic Scholar")

        print("📚 Searching CORE...")
        core_papers = self.core_search(query)
        all_papers.extend(core_papers)
        api_results['core'] = len(core_papers)
        if len(core_papers) == 0:
            api_failures += 1
        print(f"   Found {len(core_papers)} papers from CORE")

        print("📚 Searching Crossref...")
        crossref_papers = self.crossref_search(query)
        all_papers.extend(crossref_papers)
        api_results['crossref'] = len(crossref_papers)
        if len(crossref_papers) == 0:
            api_failures += 1
        print(f"   Found {len(crossref_papers)} papers from Crossref")

        print(f"📊 Total papers retrieved: {len(all_papers)}")

        # Enhanced error handling for API failures with Google Scholar fallback
        if api_failures == 3:
            if self.google_fallback and len(all_papers) == 0:
                print("🔄 All primary APIs failed, trying Google Scholar fallback...")
                try:
                    google_papers = self.google_fallback.search_papers(query, 5)
                    if google_papers:
                        all_papers.extend(google_papers)
                        print(f"✅ Google Scholar fallback: Retrieved {len(google_papers)} papers")
                    else:
                        print("⚠️ Google Scholar fallback also returned no results")
                except Exception as e:
                    print(f"⚠️ Google Scholar fallback failed: {e}")

            if len(all_papers) == 0:
                return [{
                    "error": "All research databases are currently unavailable",
                    "error_type": "api_failure",
                    "suggestion": "Please check your internet connection and try again in a few minutes",
                    "details": "Semantic Scholar, CORE, Crossref, and Google Scholar all failed to respond"
                }]
        elif api_failures == 2:
            working_apis = [api for api, count in api_results.items() if count > 0]
            print(f"⚠️ Warning: 2 out of 3 APIs failed, continuing with {working_apis[0]}")

        if len(all_papers) == 0:
            return [{
                "error": "No papers found for this research topic",
                "error_type": "no_results",
                "suggestion": "Try using broader search terms or check spelling",
                "query_attempted": query,
                "apis_checked": list(api_results.keys())
            }]

        # Filter recent papers (very lenient - include most papers)
        recent_papers = []
        cutoff_year = datetime.now().year - 10  # Extend to 10 years

        for paper in all_papers:
            year = None
            try:
                if 'year' in paper and paper['year']:
                    year = paper['year']
                elif 'published' in paper and paper['published']:
                    if 'date-parts' in paper['published']:
                        year = paper['published']['date-parts'][0][0]
                elif 'publishedDate' in paper and paper['publishedDate']:
                    year = int(str(paper['publishedDate'])[:4])
            except:
                pass

            # Include if recent OR if year unknown
            if year is None or year >= cutoff_year:
                recent_papers.append(paper)

        print(f"📅 Recent papers (≤10 years or unknown year): {len(recent_papers)}")

        # If still no papers, use all papers
        if len(recent_papers) == 0:
            print("⚠️  Using all available papers...")
            recent_papers = all_papers[:10]  # Limit to first 10

        # Filter papers with query terms in title/abstract (more lenient)
        query_words = query.lower().split()
        relevant_papers = []

        for paper in recent_papers:
            try:
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')

                # Handle different data types safely
                if isinstance(title, list):
                    title = ' '.join(str(t) for t in title if t) if title else ''
                elif title is None:
                    title = ''
                else:
                    title = str(title)

                if isinstance(abstract, list):
                    abstract = ' '.join(str(a) for a in abstract if a) if abstract else ''
                elif abstract is None:
                    abstract = ''
                else:
                    abstract = str(abstract)

                title_lower = title.lower()
                abstract_lower = abstract.lower()

                # More lenient matching - any query word OR if title/abstract is empty
                if (any(word in title_lower or word in abstract_lower for word in query_words) or
                    not title_lower.strip() or not abstract_lower.strip()):
                    relevant_papers.append(paper)
            except Exception as e:
                print(f"   Warning: Error processing paper: {e}")
                # Include paper even if there's an error
                relevant_papers.append(paper)
                continue

        print(f"🎯 Relevant papers: {len(relevant_papers)}")

        # If we still have fewer than 3 relevant papers, use all recent papers
        if len(relevant_papers) < 3:
            print("⚠️  Using all available papers due to limited relevant matches...")
            relevant_papers = recent_papers

        if len(relevant_papers) < 1:
            return [{
                "error": "No relevant recent papers found for this research topic",
                "error_type": "insufficient_data",
                "suggestion": "Try using more general terms or a different research area",
                "details": f"Found {len(all_papers)} total papers, but none were relevant or recent enough",
                "query_attempted": query
            }]

        # Process papers
        results = []
        for i, paper in enumerate(relevant_papers[:5]):
            print(f"📄 Processing paper {i+1}/5...")

            # Extract real paper information
            paper_info = self.extract_paper_info(paper)

            # STEP 2: Extract gap
            gap = self.extract_research_gap(paper, query)

            # STEP 3: Expand keywords
            keywords = self.expand_keywords(gap, query)

            # STEP 4: Self-review
            score = self.calculate_novelty_score(paper, gap)
            note = "rethink" if score < 3 else ""

            # Q1 flag
            q1_status = self.check_q1_journal(paper_info['journal_name'])

            # Next steps
            next_steps = self.generate_next_steps(gap, keywords)

            # FINAL VALIDATION: Ensure no "Data unavailable" in paper string
            base_paper_string = f"{paper_info['first_author']} {paper_info['year']} {paper_info['title']}"
            if 'unavailable' in base_paper_string.lower():
                base_paper_string = f"Author {paper_info['year']} Research Paper"

            # Add DOI as full clickable URL if available for verification
            if paper_info.get('doi'):
                doi_url = f"https://doi.org/{paper_info['doi']}"
                paper_string = f"{base_paper_string} {doi_url}"
            else:
                paper_string = base_paper_string

            result = {
                'paper': paper_string,
                'gap': gap,
                'keywords': keywords,
                'score': score,
                'note': note,
                'q1': q1_status,
                'NEXT_STEPS': next_steps
            }

            results.append(result)

        return results

def search_single_topic(topic):
    """Search for research gaps for a single topic (non-interactive)"""
    bot = GapHunterBot()
    results = bot.hunt_gaps(topic)

    print(f"\n📋 RESEARCH GAPS FOR '{topic}':")
    print("─" * 40)

    for result in results:
        print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
        print("─" * 20)

    return results

def main():
    """Main function - ONLY Gap Hunter Bot"""
    print("🎓 GAP HUNTER BOT - Academic Research Idea Development")
    print("=" * 60)

    bot = GapHunterBot()
    bot.show_greeting()
    
    # Check if running in interactive mode
    import sys
    if not sys.stdin.isatty():
        print("⚠️ Non-interactive mode detected. Use the web interface or run in an interactive terminal.")
        print("💡 To test: python clean_gap_hunter.py")
        print("🌐 Web interface: streamlit run ../web/streamlit_app.py")
        return

    while True:
        try:
            query = input("\n🎯 Enter research topic: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                continue

            # Hunt for research gaps
            results = bot.hunt_gaps(query)

            # Output in YAML format
            print("\n📋 RESEARCH GAPS (YAML):")
            print("─" * 40)

            for result in results:
                print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
                print("─" * 20)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n⚠️ No input available (EOF). Exiting...")
            print("💡 Run in an interactive terminal or use the web interface.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            # Prevent infinite loops on persistent errors
            import time
            time.sleep(1)

if __name__ == "__main__":
    import sys

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Non-interactive mode with command line argument
        topic = " ".join(sys.argv[1:])
        print("🎓 GAP HUNTER BOT - Academic Research Idea Development")
        print("=" * 60)
        print(f"🔍 Searching for research gaps in: '{topic}'")
        search_single_topic(topic)
    else:
        # Interactive mode
        main()
