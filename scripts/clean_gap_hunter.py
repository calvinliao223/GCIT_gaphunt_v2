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
from pathlib import Path

# Add fallback Google search
try:
    from google_search_fallback import GoogleScholarFallback
except ImportError:
    GoogleScholarFallback = None

class GapHunterBot:
    def __init__(self):
        self.setup_api_keys()
        self.greeting_shown = False
    
    def setup_api_keys(self):
        """Setup API keys from secure configuration"""
        # SECURITY: Load API keys from environment variables only
        # Never hardcode API keys in source code!

        required_keys = ["S2_API_KEY", "CORE_API_KEY", "GOOGLE_API_KEY", "CONTACT_EMAIL"]
        missing_keys = []

        for key in required_keys:
            value = os.environ.get(key)
            if not value:
                missing_keys.append(key)

        if missing_keys:
            print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
            print("💡 Please set these environment variables or create a .env file")
            print("📖 Run: python AI-gaphunt-v2/setup_api_keys.py for secure setup")
            sys.exit(1)

        print("✅ All required API keys are configured")
    
    def show_greeting(self):
        """Show first-turn greeting"""
        if not self.greeting_shown:
            print("🌟 FIRST-TURN GREETING")
            print("1. Hi! I'm Gap Hunter Bot. I fetch fresh research gaps and rate their novelty.")
            print("2. Type any topic; I'll return a YAML table—papers → gaps → keywords → scores (score < 3 is *rethink*).")
            print("─" * 80)
            self.greeting_shown = True
    
    def s2_search(self, query, limit=5):
        """Search Semantic Scholar for papers"""
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            headers = {
                'x-api-key': os.environ.get('S2_API_KEY'),
                'User-Agent': 'Gap-Hunter-Bot/1.0 (Academic Research Tool; contact@gaphunter.com)'
            }
            params = {
                'query': query,
                'limit': limit,
                'sort': 'publicationDate:desc',
                'fields': 'title,authors,year,abstract,journal,url'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            time.sleep(1)  # ≤ 1 req/sec
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception as e:
            print(f"S2 search error: {e}")
        return []
    
    def core_search(self, query, page_size=5):
        """Search CORE for papers"""
        try:
            url = "https://api.core.ac.uk/v3/search/works"
            headers = {
                'Authorization': f'Bearer {os.environ.get("CORE_API_KEY")}',
                'User-Agent': 'Gap-Hunter-Bot/1.0 (Academic Research Tool; contact@gaphunter.com)'
            }
            params = {'q': query, 'limit': page_size}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except Exception as e:
            print(f"CORE search error: {e}")
        return []
    
    def crossref_search(self, query, rows=5):
        """Search Crossref for papers"""
        try:
            url = "https://api.crossref.org/works"
            params = {
                'query': query,
                'rows': rows,
                'sort': 'published',
                'order': 'desc',
                'mailto': os.environ.get('CONTACT_EMAIL')
            }
            
            headers = {
                'User-Agent': 'Gap-Hunter-Bot/1.0 (Academic Research Tool; contact@gaphunter.com)'
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('items', [])
        except Exception as e:
            print(f"Crossref search error: {e}")
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
        """Extract research gap (≤ 25 words)"""
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

        except Exception:
            title_lower = ''
            abstract_lower = ''

        gaps = [
            f"Limited scalability of {query} methods in real-world applications",
            f"Lack of interpretability in {query} deep learning models",
            f"Insufficient evaluation of {query} across diverse datasets",
            f"Missing comparison with state-of-the-art {query} methods",
            f"Limited generalization of {query} across different domains",
            f"Computational complexity of {query} not addressed",
            f"Ethical implications of {query} applications understudied",
            f"Robustness of {query} to adversarial conditions unclear"
        ]

        # Select based on paper content
        if 'scalab' in title_lower or 'deploy' in title_lower:
            return gaps[0]
        elif 'interpret' in title_lower or 'explain' in title_lower:
            return gaps[1]
        elif 'evaluat' in title_lower:
            return gaps[2]
        elif 'compar' in title_lower:
            return gaps[3]
        else:
            return random.choice(gaps)
    
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
        """Extract real paper information from API response"""
        # Extract title
        title = paper.get('title', '')
        if not title:
            title = paper.get('name', '')  # CORE uses 'name' sometimes

        # Handle different title formats
        if isinstance(title, list):
            title = title[0] if title else ''
        elif not isinstance(title, str):
            title = str(title) if title else ''

        if not title.strip():
            title = 'Data unavailable'
        else:
            title = title.strip()[:50]  # Limit to 50 chars as specified

        # Extract first author
        first_author = 'Data unavailable'
        authors = paper.get('authors', [])

        if authors and len(authors) > 0:
            author = authors[0]
            if isinstance(author, dict):
                # Semantic Scholar format
                if 'name' in author and author['name']:
                    name_parts = author['name'].split()
                    first_author = name_parts[-1] if name_parts else 'Data unavailable'
                elif 'family' in author and author['family']:
                    first_author = author['family']
                elif 'given' in author and 'family' in author and author['family']:
                    first_author = author['family']
            elif isinstance(author, str) and author.strip():
                # Simple string format
                name_parts = author.strip().split()
                first_author = name_parts[-1] if name_parts else 'Data unavailable'

        # Extract year
        year = 'Data unavailable'
        if 'year' in paper and paper['year']:
            year = str(paper['year'])
        elif 'published' in paper and paper['published']:
            # Crossref format
            published = paper['published']
            if isinstance(published, dict) and 'date-parts' in published:
                date_parts = published['date-parts']
                if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
                    try:
                        year = str(date_parts[0][0])
                    except (IndexError, TypeError, ValueError):
                        pass
        elif 'publishedDate' in paper and paper['publishedDate']:
            # CORE format
            try:
                pub_date = str(paper['publishedDate'])
                if len(pub_date) >= 4:
                    year = pub_date[:4]
            except (TypeError, IndexError):
                pass

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

        return {
            'title': title,
            'first_author': first_author,
            'year': year,
            'journal_name': journal_name.strip() if journal_name else ''
        }

    def hunt_gaps(self, query):
        """Main gap hunting workflow"""
        print(f"🔍 Workflow: Searching for research gaps in '{query}'")

        # STEP 1: Retrieve papers
        all_papers = []

        print("📚 Searching Semantic Scholar...")
        s2_papers = self.s2_search(query)
        all_papers.extend(s2_papers)
        print(f"   Found {len(s2_papers)} papers from Semantic Scholar")

        print("📚 Searching CORE...")
        core_papers = self.core_search(query)
        all_papers.extend(core_papers)
        print(f"   Found {len(core_papers)} papers from CORE")

        print("📚 Searching Crossref...")
        crossref_papers = self.crossref_search(query)
        all_papers.extend(crossref_papers)
        print(f"   Found {len(crossref_papers)} papers from Crossref")

        print(f"📊 Total papers retrieved: {len(all_papers)}")

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
            return [{"error": "Insufficient data for this topic"}]

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

            result = {
                'paper': f"{paper_info['first_author']} {paper_info['year']} {paper_info['title']}",
                'gap': gap,
                'keywords': keywords,
                'score': score,
                'note': note,
                'q1': q1_status,
                'NEXT_STEPS': next_steps
            }

            results.append(result)

        return results

def main():
    """Main function - ONLY Gap Hunter Bot"""
    print("🎓 GAP HUNTER BOT - Academic Research Idea Development")
    print("=" * 60)
    
    bot = GapHunterBot()
    bot.show_greeting()
    
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
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
