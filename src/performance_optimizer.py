#!/usr/bin/env python3
"""
Performance optimization utilities for Gap Hunter Bot
Provides caching, connection pooling, and async operations
"""

import asyncio
import aiohttp
import time
import functools
import hashlib
import json
import os
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._lock = threading.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() < entry['expires']:
                    return entry['value']
                else:
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        expires = datetime.now() + timedelta(seconds=ttl)
        
        with self._lock:
            self.cache[key] = {
                'value': value,
                'expires': expires
            }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = datetime.now()
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if now >= entry['expires']
            ]
            for key in expired_keys:
                del self.cache[key]

# Global cache instance
_cache = MemoryCache()

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom function to generate cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _cache._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

class ConnectionPool:
    """HTTP connection pool for efficient API requests"""
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request using connection pool"""
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request using connection pool"""
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session"""
        self.session.close()

# Global connection pool
_connection_pool = ConnectionPool()

class AsyncAPIClient:
    """Async API client for concurrent requests"""
    
    def __init__(self, timeout: int = 30, max_concurrent: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch(self, session: aiohttp.ClientSession, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch single URL"""
        async with self.semaphore:
            try:
                async with session.get(url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}"}
            except Exception as e:
                return {"error": str(e)}
    
    async def fetch_multiple(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch multiple URLs concurrently"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = []
            for req in requests:
                task = self.fetch(session, **req)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

def batch_api_requests(requests: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """
    Execute multiple API requests concurrently
    
    Args:
        requests: List of request dictionaries with 'url' and optional params
        max_concurrent: Maximum concurrent requests
    
    Returns:
        List of response dictionaries
    """
    client = AsyncAPIClient(max_concurrent=max_concurrent)
    
    # Run async function in event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(client.fetch_multiple(requests))

def rate_limit(calls_per_second: float = 1.0):
    """
    Decorator for rate limiting function calls
    
    Args:
        calls_per_second: Maximum calls per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

def profile_performance(func: Callable) -> Callable:
    """Decorator to profile function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = _get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = e
            success = False
        
        end_time = time.time()
        end_memory = _get_memory_usage()
        
        # Log performance metrics
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory
        
        print(f"Performance: {func.__name__}")
        print(f"  Time: {execution_time:.3f}s")
        print(f"  Memory: {memory_delta:.2f}MB")
        print(f"  Status: {'SUCCESS' if success else 'FAILED'}")
        
        if not success:
            raise result
        
        return result
    return wrapper

def _get_memory_usage() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0

class QueryOptimizer:
    """Optimize search queries for better performance"""
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize search query for better API performance"""
        if not query:
            return query
        
        # Remove common stop words that don't add value
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        
        words = query.lower().split()
        optimized_words = [word for word in words if word not in stop_words]
        
        # Keep at least 2 words
        if len(optimized_words) < 2 and len(words) >= 2:
            optimized_words = words[:2]
        
        return ' '.join(optimized_words)
    
    @staticmethod
    def extract_key_terms(query: str, max_terms: int = 5) -> List[str]:
        """Extract key terms from query for focused search"""
        if not query:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = query.lower().split()
        
        # Filter out short words and common terms
        key_words = [
            word for word in words 
            if len(word) > 3 and word.isalpha()
        ]
        
        return key_words[:max_terms]

class ResultsOptimizer:
    """Optimize processing of search results"""
    
    @staticmethod
    def deduplicate_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity"""
        if not papers:
            return papers
        
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            if not title:
                continue
            
            # Simple deduplication based on title
            title_key = ''.join(title.split())  # Remove spaces
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_papers.append(paper)
        
        return unique_papers
    
    @staticmethod
    def prioritize_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize papers based on relevance indicators"""
        if not papers:
            return papers
        
        def get_priority_score(paper: Dict[str, Any]) -> float:
            score = 0.0
            
            # Recent papers get higher priority
            year = paper.get('year', 0)
            if year >= 2020:
                score += 2.0
            elif year >= 2015:
                score += 1.0
            
            # Papers with abstracts get higher priority
            if paper.get('abstract'):
                score += 1.0
            
            # Papers with citation count get higher priority
            citations = paper.get('citationCount', 0)
            if citations > 100:
                score += 2.0
            elif citations > 10:
                score += 1.0
            
            return score
        
        # Sort by priority score (descending)
        return sorted(papers, key=get_priority_score, reverse=True)

# Utility functions for performance monitoring
def clear_cache():
    """Clear the global cache"""
    _cache.clear()

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    with _cache._lock:
        return {
            'entries': len(_cache.cache),
            'memory_usage_mb': _get_memory_usage()
        }

def cleanup_resources():
    """Cleanup performance optimization resources"""
    _cache.clear()
    _connection_pool.close()

# Context manager for performance optimization
class PerformanceContext:
    """Context manager for performance-optimized operations"""
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        print(f"Operation completed in {execution_time:.3f}s")
        
        # Cleanup expired cache entries
        _cache.cleanup_expired()

# Example usage functions
def optimize_gap_hunter_search(query: str, apis: List[str]) -> List[Dict[str, Any]]:
    """
    Optimized search across multiple APIs
    
    Args:
        query: Search query
        apis: List of API names to search
    
    Returns:
        Combined and optimized results
    """
    optimizer = QueryOptimizer()
    results_optimizer = ResultsOptimizer()
    
    # Optimize query
    optimized_query = optimizer.optimize_query(query)
    
    # Prepare concurrent requests
    requests = []
    for api in apis:
        if api == 's2':
            requests.append({
                'url': 'https://api.semanticscholar.org/graph/v1/paper/search',
                'params': {'query': optimized_query, 'limit': 10}
            })
        elif api == 'core':
            requests.append({
                'url': 'https://api.core.ac.uk/v3/search/works',
                'params': {'q': optimized_query, 'limit': 10}
            })
    
    # Execute concurrent requests
    with PerformanceContext():
        results = batch_api_requests(requests)
    
    # Process and optimize results
    all_papers = []
    for result in results:
        if 'data' in result:
            all_papers.extend(result['data'])
        elif 'results' in result:
            all_papers.extend(result['results'])
    
    # Deduplicate and prioritize
    unique_papers = results_optimizer.deduplicate_papers(all_papers)
    prioritized_papers = results_optimizer.prioritize_papers(unique_papers)
    
    return prioritized_papers[:20]  # Return top 20 results
