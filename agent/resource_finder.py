"""Resource finder using DuckDuckGo search."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from ddgs.ddgs import DDGS
import time
import re


@dataclass
class LearningResource:
    """Represents a learning resource found via search."""
    title: str
    url: str
    description: str
    source: str = "web"


class ResourceFinder:
    """Finds learning resources using DuckDuckGo search."""
    
    def __init__(self, max_results_per_concept: int = 5):
        """Initialize resource finder.
        
        Args:
            max_results_per_concept: Maximum number of results to return per concept
        """
        self.max_results = max_results_per_concept
        self.ddgs = DDGS()
    
    def find_resources_for_concept(self, concept_name: str) -> List[LearningResource]:
        """Find learning resources for a specific concept.
        
        Args:
            concept_name: The concept or technology to search for
            
        Returns:
            List of LearningResource objects
        """
        scored_resources = []  # Store as (score, resource) tuples
        debug_counts = {
            'total_results': 0,
            'filtered_duplicate': 0,
            'filtered_invalid_url': 0,
            'filtered_stackoverflow': 0,
            'filtered_irrelevant': 0,
            'filtered_invalid_resource': 0,
            'accepted': 0
        }
        
        # Multiple search queries to get diverse educational results (prioritize tutorials and courses)
        search_queries = [
            f"{concept_name} tutorial",
            f"learn {concept_name}",
            f"{concept_name} documentation",
            f"{concept_name} course",
            f"{concept_name} getting started guide"
        ]
        
        seen_urls = set()
        
        for query in search_queries:
            try:
                results = self.ddgs.text(query, max_results=5)  # Get more results to filter from
                results_list = list(results) if results else []
                
                for result in results_list:
                    debug_counts['total_results'] += 1
                    url = result.get("href", "")
                    title = result.get("title", "")
                    body = result.get("body", "")
                    
                    # Skip duplicates and invalid results
                    if url in seen_urls or not url or not title:
                        debug_counts['filtered_duplicate'] += 1
                        continue
                    
                    # Filter out Stack Overflow completely
                    if "stackoverflow.com" in url.lower():
                        debug_counts['filtered_stackoverflow'] += 1
                        continue
                    
                    # Check relevance - title or URL should contain concept keywords
                    concept_lower = concept_name.lower()
                    title_lower = title.lower()
                    url_lower = url.lower()
                    
                    # Extract main keywords from concept (remove common words and parentheses content)
                    # Handle complex names like "Python ML ecosystem (NumPy, Matplotlib, PIL/OpenCV)"
                    concept_clean = re.sub(r'\([^)]*\)', '', concept_lower)  # Remove parentheses content
                    concept_words = [w for w in concept_clean.split() if w not in ['the', 'a', 'an', 'and', 'or', 'for', 'with', 'development', 'basics', 'fundamentals', '&', 'and', 'environment']]
                    # Also extract words from parentheses if they exist
                    paren_match = re.search(r'\(([^)]+)\)', concept_lower)
                    if paren_match:
                        paren_words = [w.strip() for w in paren_match.group(1).replace('/', ' ').replace(',', ' ').split()]
                        concept_words.extend([w.lower() for w in paren_words if len(w) > 2])
                    
                    # More lenient relevance check - check if ANY significant word matches
                    # This allows results that match part of the concept name
                    if concept_words:
                        is_relevant = (
                            any(word in title_lower for word in concept_words[:5]) or  # Check first 5 words
                            any(word in url_lower for word in concept_words[:5]) or
                            concept_words[0] in title_lower or  # Main keyword
                            concept_words[0] in url_lower
                        )
                    else:
                        # Fallback: if no words extracted, check if concept name appears
                        is_relevant = concept_lower[:20] in title_lower or concept_lower[:20] in url_lower
                    
                    if not is_relevant:
                        debug_counts['filtered_irrelevant'] += 1
                        continue
                    
                    # Score resources - prioritize educational content over Stack Overflow
                    resource_score = self._score_learning_resource(url, title, concept_name)
                    
                    # Check if resource is valid (this also filters out Stack Overflow)
                    if self._is_valid_learning_resource(url, title, concept_name):
                        # Accept resources with score >= 0 (very permissive, but we still filter out bad domains)
                        if resource_score >= 0:
                            resource = LearningResource(
                                title=title,
                                url=url,
                                description=body[:200] + "..." if len(body) > 200 else body,
                                source="web"
                            )
                            # Store score for sorting
                            scored_resources.append((resource_score, resource))
                            seen_urls.add(url)
                            debug_counts['accepted'] += 1
                    else:
                        debug_counts['filtered_invalid_resource'] += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                # Continue with next query if one fails
                print(f"  Warning: Search failed for '{query}': {e}")
                continue
        
        # Sort by score (highest first) and take top results
        scored_resources.sort(key=lambda x: x[0], reverse=True)
        resources = [r[1] for r in scored_resources[:self.max_results]]
        
        # Debug: Show how many resources found
        if len(resources) == 0:
            print(f"    ⚠️  No resources found for '{concept_name}'")
            print(f"       Debug: {debug_counts['total_results']} results, "
                  f"{debug_counts['filtered_stackoverflow']} SO, "
                  f"{debug_counts['filtered_irrelevant']} irrelevant, "
                  f"{debug_counts['filtered_invalid_resource']} invalid, "
                  f"{debug_counts['filtered_duplicate']} dup")
        else:
            print(f"    ✓ Found {len(resources)} resource(s)")
        
        return resources
    
    def find_resources_for_prerequisites(self, prerequisites: List) -> Dict[str, List[LearningResource]]:
        """Find resources for multiple prerequisites.
        
        Args:
            prerequisites: List of Prerequisite objects
            
        Returns:
            Dictionary mapping prerequisite names to their resources
        """
        resources_by_concept = {}
        
        # Limit to top 10 prerequisites by priority to avoid too many searches
        sorted_prereqs = sorted(prerequisites, key=lambda x: x.priority)[:10]
        
        for prereq in sorted_prereqs:
            concept_name = prereq.name
            print(f"  Searching for: {concept_name}...")
            
            resources = self.find_resources_for_concept(concept_name)
            resources_by_concept[concept_name] = resources
            
            # Small delay between concepts
            time.sleep(0.3)
        
        return resources_by_concept
    
    def _score_learning_resource(self, url: str, title: str, concept_name: str = "") -> int:
        """Score a learning resource based on educational value.
        
        Args:
            url: URL to check
            title: Page title
            concept_name: The concept being searched for
            
        Returns:
            Score (higher is better, 0 = exclude)
        """
        url_lower = url.lower()
        title_lower = title.lower()
        score = 1  # Start with base score of 1 to ensure resources pass the threshold
        
        # High-value educational domains (score +10)
        high_value_domains = [
            "docs.", "documentation",
            "tutorialspoint.com",
            "w3schools.com",
            "freecodecamp.org",
            "codecademy.com",
            "coursera.org",
            "udemy.com",
            "edx.org",
            "khanacademy.org",
            "pluralsight.com",
            "realpython.com",
            "javascript.info",
            "react.dev",
            "djangoproject.com",
            "python.org",
            "developer.mozilla.org",
            "web.dev",
            "geeksforgeeks.org",
            "mdn",
            "learn.microsoft.com",
            "tensorflow.org",
            "keras.io",
            "pytorch.org",
            "scikit-learn.org",
            "numpy.org",
            "matplotlib.org",
            "pandas.pydata.org",
            "tutorial",
            "guide",
            "getting-started"
        ]
        
        for domain in high_value_domains:
            if domain in url_lower or domain in title_lower:
                score += 10
                break
        
        # Medium-value educational domains (score +5)
        medium_value_domains = [
            "github.com",
            "medium.com",
            "dev.to",
            "towardsdatascience.com",
            "css-tricks.com",
            "smashingmagazine.com"
        ]
        
        for domain in medium_value_domains:
            if domain in url_lower or domain in title_lower:
                score += 5
                break
        
        # Stack Overflow is completely excluded (filtered out earlier)
        
        # Educational keywords in title (score +3)
        educational_keywords = [
            "tutorial", "learn", "course", "documentation", "guide",
            "getting started", "introduction", "basics", "fundamentals",
            "how to", "example", "reference", "docs"
        ]
        
        if any(keyword in title_lower for keyword in educational_keywords):
            score += 3
        
        # Concept name in title (score +2)
        concept_lower = concept_name.lower() if concept_name else ""
        # Clean concept name (remove parentheses content for matching)
        concept_clean = re.sub(r'\([^)]*\)', '', concept_lower)
        concept_words = [w for w in concept_clean.split() if w not in ['the', 'a', 'an', 'and', 'or', 'for', 'with', '&']]
        if concept_words:
            # Check if any main concept words appear in title
            if any(word in title_lower for word in concept_words[:3]):
                score += 2
            # Also check for words from parentheses if they exist
            paren_match = re.search(r'\(([^)]+)\)', concept_lower)
            if paren_match:
                paren_words = [w.strip().lower() for w in paren_match.group(1).replace('/', ' ').replace(',', ' ').split() if len(w.strip()) > 2]
                if any(word in title_lower for word in paren_words[:2]):
                    score += 2
        
        # Penalize low-quality indicators
        low_quality_indicators = [
            "question", "answer", "error", "problem", "issue", "bug",
            "why does", "how do i", "what is the difference"
        ]
        
        if any(indicator in title_lower for indicator in low_quality_indicators):
            score -= 2
        
        return max(0, score)  # Don't return negative scores
    
    def _is_valid_learning_resource(self, url: str, title: str, concept_name: str = "") -> bool:
        """Check if a URL appears to be a valid learning resource.
        
        Args:
            url: URL to check
            title: Page title
            concept_name: The concept being searched for (for relevance check)
            
        Returns:
            True if appears to be a valid English learning resource
        """
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Filter out non-English domains (Chinese, Russian, etc.)
        non_english_domains = [
            "zhihu.com",      # Chinese Q&A
            "baidu.com",      # Chinese search engine
            "zhidao.baidu.com",  # Chinese Q&A
            "douban.com",     # Chinese social network
            "weibo.com",      # Chinese social network
            "qq.com",         # Chinese portal
            "163.com",        # Chinese portal
            "sina.com.cn",    # Chinese portal
            "sohu.com",       # Chinese portal
            "yandex.ru",      # Russian search engine
            "mail.ru",        # Russian portal
            "rambler.ru",     # Russian portal
            "naver.com",      # Korean portal
            "daum.net",       # Korean portal
            ".jp/",           # Japanese sites
            ".kr/",           # Korean sites
            ".cn/",           # Chinese sites
            ".ru/",           # Russian sites
        ]
        
        for domain in non_english_domains:
            if domain in url_lower:
                return False
        
        # Filter out common non-educational domains and low-quality sources
        excluded_domains = [
            "stackoverflow.com",  # Stack Overflow Q&A (not learning resources)
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "linkedin.com",
            "pinterest.com",
            "reddit.com",
            "youtube.com/watch",  # We want YouTube but not specific videos
            "learn.lboro.ac.uk",  # University LMS (not public learning resources)
            "blackboard.com",
            "canvas.net",
            "moodle.org",
            "brightspace.com",
            "support.google.com",  # Google support pages (not learning resources)
            "support.microsoft.com",
            "help.",  # Generic help pages
        ]
        
        for domain in excluded_domains:
            if domain in url_lower:
                return False
        
        # Check for non-English characters in title (basic heuristic)
        # Filter out titles with too many non-ASCII characters (likely non-English)
        non_ascii_count = sum(1 for c in title if ord(c) > 127)
        if len(title) > 0 and non_ascii_count / len(title) > 0.3:  # More than 30% non-ASCII
            return False
        
        # Prefer educational domains
        educational_domains = [
            "github.com",
            "stackoverflow.com",
            "docs.",
            "tutorial",
            "learn",
            "course",
            "documentation",
            "guide",
            "w3schools",
            "mdn",
            "freecodecamp",
            "coursera",
            "udemy",
            "edx",
            "khanacademy",
            "medium.com",
            "dev.to",
            "towardsdatascience.com",
            "geeksforgeeks.org",
            "tutorialspoint.com",
            "codecademy.com",
            "pluralsight.com",
            "realpython.com",
            "javascript.info",
            "react.dev",
            "djangoproject.com",
            "python.org",
            "nodejs.org",
            "developer.mozilla.org",
            "web.dev",
            "css-tricks.com",
            "smashingmagazine.com"
        ]
        
        # Check if URL or title contains educational keywords
        for domain in educational_domains:
            if domain in url_lower or domain in title_lower:
                return True
        
        # Additional quality checks
        # Filter out generic/university LMS pages (but allow public educational content)
        low_quality_indicators = [
            "course/index.php",
            "/lms/",
            "/blackboard/",
            "/moodle/",
            "/canvas/",
            "/brightspace/",
            "student portal",
            "enrollment",
            "registration",
            "login",
            "sign in",
            "my courses"  # LMS-specific pages
        ]
        
        # Only filter if URL path contains LMS indicators (not just domain)
        url_path = url_lower.split('/', 3)[-1] if '/' in url_lower else ""
        is_lms_page = any(indicator in url_path or indicator in title_lower for indicator in low_quality_indicators)
        
        if is_lms_page:
            return False
        
        # Require that the title contains educational keywords or the concept
        educational_keywords = [
            "tutorial", "learn", "course", "documentation", "guide", 
            "getting started", "introduction", "basics", "fundamentals",
            "how to", "example", "reference", "api", "docs", "training",
            "getting-started", "beginner", "overview", "crash course",
            "handbook", "manual", "book", "library", "framework"
        ]
        
        concept_lower = concept_name.lower() if concept_name else ""
        concept_words = concept_lower.split() if concept_lower else []
        
        has_educational_keyword = any(keyword in title_lower for keyword in educational_keywords)
        # More lenient concept matching - check first 3 words
        concept_clean = re.sub(r'\([^)]*\)', '', concept_lower) if concept_lower else ""
        concept_words_clean = [w for w in concept_clean.split() if w not in ['the', 'a', 'an', 'and', 'or', 'for', 'with', '&']]
        has_concept_in_title = any(word in title_lower for word in concept_words_clean[:3]) if concept_words_clean else False
        
        # More lenient: allow resources through if they pass basic checks
        # Don't require both educational domain AND keywords - either one is sufficient
        has_educational_domain = any(domain in url_lower or domain in title_lower for domain in educational_domains)
        
        if not has_educational_domain and not has_educational_keyword and not has_concept_in_title:
            # Only reject if it has none of: educational domain, educational keyword, or concept match
            return False
        
        # Basic check: URL should be in English (no non-English TLDs)
        english_tlds = [".com", ".org", ".net", ".io", ".dev", ".edu", ".co.uk"]
        has_english_tld = any(tld in url_lower for tld in english_tlds)
        
        return has_english_tld

