# backend/arxiv_importer/core/keyword_manager.py
import os
import json
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction process"""
    primary_keywords: List[str]
    secondary_keywords: List[str]
    technical_terms: List[str]
    domain_tags: List[str]
    confidence_score: float
    extraction_method: str


class KeywordManager:
    """Advanced keyword management system for scientific papers"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.quantum_domains = self._load_quantum_domains()
        self.technical_terms = self._load_technical_terms()
        self.stop_words = self._load_stop_words()

    def _load_quantum_domains(self) -> List[str]:
        """Load quantum computing domain categories"""
        return [
            "Quantum Computing", "Quantum Algorithm", "Quantum Hardware",
            "Quantum Communication", "Quantum Key Distribution (QKD)",
            "Post Quantum Cryptography (PQC)", "Quantum Error Correction",
            "Noisy Intermediate-Scale Quantum (NISQ)", "Quantum Benchmarking",
            "Quantum AI", "Quantum Blockchain", "Quantum Networking",
            "Quantum Cloud Computing", "Quantum Operating Systems",
            "Quantum Programming Languages", "Quantum Supremacy and Advantage"
        ]

    def _load_technical_terms(self) -> Set[str]:
        """Load technical terms from various sources"""
        return {
            "IBM Qiskit", "Google Cirq", "Rigetti Forest", "Microsoft Q#",
            "Xanadu PennyLane", "Amazon Braket", "D-Wave Ocean SDK",
            "QuTiP", "ProjectQ", "OpenFermion", "quantum circuit",
            "quantum gate", "quantum state", "entanglement", "superposition",
            "decoherence", "quantum annealing", "adiabatic quantum computing",
            "variational quantum eigensolver", "quantum approximate optimization",
            "quantum machine learning", "quantum neural networks"
        }

    def _load_stop_words(self) -> Set[str]:
        """Load stop words for keyword filtering"""
        return {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "before", "after", "above", "below", "between", "among", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "could", "should", "may", "might", "must", "can"
        }

    def extract_keywords_from_text(self, text: str, title: str = "", abstract: str = "") -> KeywordExtractionResult:
        """
        Extract keywords from paper text using multiple methods
        """
        # Combine all text sources
        full_text = f"{title}\n{abstract}\n{text}".strip()

        # Method 1: AI-powered extraction
        ai_keywords = self._extract_with_ai(full_text)

        # Method 2: Technical term detection
        technical_terms = self._extract_technical_terms(full_text)

        # Method 3: Domain classification
        domain_tags = self._classify_domains(full_text)

        # Method 4: Statistical keyword extraction
        statistical_keywords = self._extract_statistical_keywords(full_text)

        # Combine and rank results
        return self._combine_and_rank_keywords(
            ai_keywords, technical_terms, domain_tags, statistical_keywords
        )

    def _extract_with_ai(self, text: str) -> Dict[str, Any]:
        """Extract keywords using OpenAI GPT-4"""
        try:
            system_prompt = """You are a scientific keyword extraction expert specializing in quantum computing and cybersecurity.
            
            Extract keywords from the given text and return a JSON object with:
            - "primary_keywords": 5-8 most important keywords (high relevance)
            - "secondary_keywords": 5-10 additional relevant keywords (medium relevance)
            - "technical_terms": specific technical terms found
            - "domain_tags": relevant domain categories from quantum computing
            
            Focus on:
            - Quantum computing concepts and algorithms
            - Cybersecurity and cryptography terms
            - Technical implementations and frameworks
            - Research methodologies and applications
            
            Return only valid JSON, no additional text."""

            # Limit text length
            user_prompt = f"Extract keywords from this scientific text:\n\n{text[:4000]}"

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content.strip())
            return result

        except Exception as e:
            print(f"AI keyword extraction failed: {e}")
            return {
                "primary_keywords": [],
                "secondary_keywords": [],
                "technical_terms": [],
                "domain_tags": []
            }

    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms using pattern matching"""
        found_terms = []
        text_lower = text.lower()

        for term in self.technical_terms:
            if term.lower() in text_lower:
                found_terms.append(term)

        return found_terms

    def _classify_domains(self, text: str) -> List[str]:
        """Classify paper into quantum computing domains"""
        text_lower = text.lower()
        relevant_domains = []

        for domain in self.quantum_domains:
            # Check for domain-specific keywords
            domain_keywords = self._get_domain_keywords(domain)
            if any(keyword.lower() in text_lower for keyword in domain_keywords):
                relevant_domains.append(domain)

        return relevant_domains

    def _get_domain_keywords(self, domain: str) -> List[str]:
        """Get keywords associated with a specific domain"""
        domain_keyword_map = {
            "Quantum Computing": ["quantum computer", "quantum processor", "quantum system"],
            "Quantum Algorithm": ["quantum algorithm", "quantum circuit", "quantum gate"],
            "Quantum Communication": ["quantum communication", "quantum channel", "quantum network"],
            "Post Quantum Cryptography (PQC)": ["post-quantum", "quantum-resistant", "lattice-based"],
            "Quantum Error Correction": ["quantum error", "error correction", "quantum fault tolerance"],
            "Quantum AI": ["quantum machine learning", "quantum neural network", "quantum optimization"]
        }

        return domain_keyword_map.get(domain, [domain.lower()])

    def _extract_statistical_keywords(self, text: str) -> List[str]:
        """Extract keywords using statistical methods (TF-IDF-like)"""
        # Simple word frequency analysis
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Filter out stop words and count frequencies
        word_freq = {}
        for word in words:
            if word not in self.stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top 10 most frequent words
        sorted_words = sorted(
            word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 1]

    def _combine_and_rank_keywords(self, ai_result: Dict, technical_terms: List[str],
                                   domain_tags: List[str], statistical_keywords: List[str]) -> KeywordExtractionResult:
        """Combine and rank all extracted keywords"""

        # Primary keywords (AI + Technical terms + Domains)
        primary = list(set(
            ai_result.get("primary_keywords", []) +
            technical_terms[:3] +  # Top 3 technical terms
            domain_tags[:2]  # Top 2 domains
        ))

        # Secondary keywords (AI secondary + Statistical)
        secondary = list(set(
            ai_result.get("secondary_keywords", []) +
            statistical_keywords[:5]  # Top 5 statistical keywords
        ))

        # Technical terms (deduplicated)
        technical = list(set(technical_terms))

        # Domain tags (deduplicated)
        domains = list(set(domain_tags))

        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            primary, secondary, technical, domains)

        return KeywordExtractionResult(
            primary_keywords=primary[:8],  # Limit to 8
            secondary_keywords=secondary[:10],  # Limit to 10
            technical_terms=technical,
            domain_tags=domains,
            confidence_score=confidence,
            extraction_method="hybrid_ai_statistical"
        )

    def _calculate_confidence_score(self, primary: List[str], secondary: List[str],
                                    technical: List[str], domains: List[str]) -> float:
        """Calculate confidence score for keyword extraction"""
        total_keywords = len(primary) + len(secondary) + \
            len(technical) + len(domains)

        if total_keywords == 0:
            return 0.0

        # Higher confidence if we have technical terms and domains
        technical_bonus = len(technical) * 0.1
        domain_bonus = len(domains) * 0.15

        # Base score from quantity
        base_score = min(0.7, total_keywords * 0.05)
        confidence = min(1.0, base_score + technical_bonus + domain_bonus)

        return round(confidence, 2)

    def suggest_keywords_for_paper(self, paper_data: Dict[str, Any]) -> KeywordExtractionResult:
        """Main method to suggest keywords for a paper"""
        # Convert Pydantic model to dict if needed
        if hasattr(paper_data, 'model_dump'):
            paper_dict = paper_data.model_dump()
        elif hasattr(paper_data, 'dict'):
            paper_dict = paper_data.dict()
        else:
            paper_dict = paper_data

        title = paper_dict.get("title", "")
        abstract = paper_dict.get("summary", "")

        # Extract text from paper (if available)
        text = f"{title}\n{abstract}"

        return self.extract_keywords_from_text(text, title, abstract)

    def validate_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Validate and normalize keywords"""
        validated = {
            "valid_keywords": [],
            "invalid_keywords": [],
            "suggestions": [],
            "normalized_keywords": []
        }

        for keyword in keywords:
            keyword = keyword.strip()

            # Check if keyword is valid
            if len(keyword) < 2 or len(keyword) > 50:
                validated["invalid_keywords"].append(keyword)
                continue

            # Normalize keyword
            normalized = self._normalize_keyword(keyword)
            validated["normalized_keywords"].append(normalized)

            # Check if it's a known technical term
            if normalized.lower() in [term.lower() for term in self.technical_terms]:
                validated["valid_keywords"].append(normalized)
            else:
                # Suggest similar terms
                suggestions = self._suggest_similar_terms(normalized)
                validated["suggestions"].append({
                    "original": normalized,
                    "suggestions": suggestions
                })

        return validated

    def _normalize_keyword(self, keyword: str) -> str:
        """Normalize keyword format"""
        # Remove extra spaces, convert to title case for proper nouns
        normalized = " ".join(keyword.split())

        # Handle special cases
        if "quantum" in normalized.lower():
            normalized = normalized.replace("quantum", "Quantum")

        return normalized

    def _suggest_similar_terms(self, keyword: str) -> List[str]:
        """Suggest similar technical terms"""
        keyword_lower = keyword.lower()
        suggestions = []

        for term in self.technical_terms:
            if keyword_lower in term.lower() or term.lower() in keyword_lower:
                suggestions.append(term)

        return suggestions[:3]  # Return top 3 suggestions


# Create global instance
keyword_manager = KeywordManager()
