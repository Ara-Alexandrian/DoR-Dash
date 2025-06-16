"""
Knowledge Base Service for DoR-Dash
Extracts and manages domain-specific terminology from user submissions
"""

import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
import sqlite3
import os
from pathlib import Path

# Scientific/Medical terminology patterns
DOMAIN_PATTERNS = {
    'medical_terms': [
        r'\b(?:carcinoma|sarcoma|melanoma|lymphoma|leukemia)\b',
        r'\b(?:chemotherapy|radiotherapy|immunotherapy|targeted therapy)\b',
        r'\b(?:metastasis|metastatic|invasion|angiogenesis)\b',
        r'\b(?:oncology|oncologist|tumor|malignant|benign)\b',
        r'\b(?:biopsy|histology|pathology|cytology)\b'
    ],
    'research_methods': [
        r'\b(?:Western blot|PCR|qPCR|RT-PCR|ELISA|immunofluorescence)\b',
        r'\b(?:MTT assay|flow cytometry|microscopy|spectroscopy)\b',
        r'\b(?:cell culture|transfection|knockout|overexpression)\b',
        r'\b(?:statistical analysis|p-value|significance|correlation)\b',
        r'\b(?:ANOVA|t-test|Mann-Whitney|Wilcoxon)\b'
    ],
    'abbreviations': [
        r'\b[A-Z]{2,6}\b',  # General abbreviations (2-6 caps)
        r'\b(?:DNA|RNA|mRNA|siRNA|miRNA|lncRNA)\b',
        r'\b(?:ATP|ADP|NADH|FADH2|ROS)\b',
        r'\b(?:DMSO|PBS|EDTA|Tris|BSA)\b'
    ],
    'technical_terms': [
        r'\b(?:dose-response|concentration|dilution|gradient)\b',
        r'\b(?:proliferation|differentiation|apoptosis|necrosis)\b',
        r'\b(?:signaling pathway|cascade|upstream|downstream)\b',
        r'\b(?:biomarker|endpoint|outcome|efficacy)\b'
    ],
    'funding_terms': [
        r'\b(?:NIH|NSF|DoD|CPRIT|R01|R21|R03)\b',
        r'\b(?:grant|funding|budget|proposal|application)\b',
        r'\b(?:preliminary data|pilot study|feasibility)\b'
    ]
}

# Common academic writing improvements
WRITING_PATTERNS = {
    'weak_words': ['very', 'really', 'quite', 'pretty', 'somewhat'],
    'filler_words': ['obviously', 'basically', 'actually', 'literally'],
    'passive_indicators': ['was performed', 'was conducted', 'was observed'],
    'hedge_words': ['might', 'could', 'possibly', 'perhaps', 'maybe']
}

@dataclass
class TerminologyEntry:
    term: str
    category: str
    frequency: int
    contexts: List[str]
    first_seen: datetime
    last_seen: datetime
    confidence_score: float
    user_approved: bool = False

@dataclass
class KnowledgeSnapshot:
    timestamp: datetime
    total_submissions: int
    new_terms_found: int
    updated_terms: int
    top_terms: List[Tuple[str, int]]

class KnowledgeBaseService:
    def __init__(self, db_path: str = "/app/data/knowledge_base.db"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create database tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS terminology (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    contexts TEXT,  -- JSON array of context strings
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL DEFAULT 0.5,
                    user_approved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_submissions INTEGER,
                    new_terms_found INTEGER,
                    updated_terms INTEGER,
                    top_terms TEXT,  -- JSON array
                    summary TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_term ON terminology(term);
                CREATE INDEX IF NOT EXISTS idx_category ON terminology(category);
                CREATE INDEX IF NOT EXISTS idx_frequency ON terminology(frequency DESC);
            ''')
    
    def extract_terminology(self, text: str) -> Dict[str, List[str]]:
        """Extract domain-specific terminology from text"""
        found_terms = defaultdict(list)
        text_lower = text.lower()
        
        # Extract terms by category
        for category, patterns in DOMAIN_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    found_terms[category].append(match.lower())
        
        # Extract capitalized terms that might be proper nouns or technical terms
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for term in capitalized_terms:
            if len(term) > 3 and term.lower() not in ['The', 'This', 'That', 'They', 'Then']:
                found_terms['proper_nouns'].append(term.lower())
        
        # Extract potential new abbreviations
        new_abbrevs = re.findall(r'\b[A-Z]{2,5}\b', text)
        for abbrev in new_abbrevs:
            if abbrev not in ['DNA', 'RNA', 'ATP', 'NIH', 'PCR']:  # Skip common ones
                found_terms['new_abbreviations'].append(abbrev)
        
        return dict(found_terms)
    
    def analyze_writing_quality(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for writing quality issues"""
        issues = defaultdict(list)
        text_lower = text.lower()
        
        # Check for weak words
        for word in WRITING_PATTERNS['weak_words']:
            if word in text_lower:
                issues['weak_words'].append(word)
        
        # Check for filler words
        for word in WRITING_PATTERNS['filler_words']:
            if word in text_lower:
                issues['filler_words'].append(word)
        
        # Check for passive voice indicators
        for phrase in WRITING_PATTERNS['passive_indicators']:
            if phrase in text_lower:
                issues['passive_voice'].append(phrase)
        
        return dict(issues)
    
    def update_terminology_db(self, terms: Dict[str, List[str]], context: str):
        """Update the terminology database with new findings"""
        with sqlite3.connect(self.db_path) as conn:
            for category, term_list in terms.items():
                for term in term_list:
                    # Check if term exists
                    existing = conn.execute(
                        'SELECT id, frequency, contexts FROM terminology WHERE term = ?',
                        (term,)
                    ).fetchone()
                    
                    if existing:
                        # Update existing term
                        term_id, frequency, contexts_json = existing
                        contexts = json.loads(contexts_json) if contexts_json else []
                        contexts.append(context[:100])  # Keep context snippets short
                        if len(contexts) > 10:  # Limit context history
                            contexts = contexts[-10:]
                        
                        conn.execute('''
                            UPDATE terminology 
                            SET frequency = frequency + 1, 
                                last_seen = CURRENT_TIMESTAMP,
                                contexts = ?,
                                confidence_score = MIN(1.0, confidence_score + 0.1)
                            WHERE id = ?
                        ''', (json.dumps(contexts), term_id))
                    else:
                        # Insert new term
                        conn.execute('''
                            INSERT INTO terminology 
                            (term, category, contexts, confidence_score)
                            VALUES (?, ?, ?, ?)
                        ''', (term, category, json.dumps([context[:100]]), 0.3))
    
    async def snapshot_submissions(self) -> KnowledgeSnapshot:
        """Analyze all recent submissions and update knowledge base"""
        from app.db.models.user import SessionLocal
        from app.db.models.user import StudentUpdate, FacultyUpdate
        
        snapshot_time = datetime.now()
        new_terms = 0
        updated_terms = 0
        
        with SessionLocal() as db:
            # Get recent submissions (last 30 days)
            recent_date = snapshot_time - timedelta(days=30)
            
            # Analyze student updates
            student_updates = db.query(StudentUpdate).filter(
                StudentUpdate.created_at >= recent_date
            ).all()
            
            for update in student_updates:
                # Combine all text fields
                combined_text = f"{update.progress_text or ''} {update.challenges_text or ''} {update.next_steps_text or ''}"
                
                if combined_text.strip():
                    terms = self.extract_terminology(combined_text)
                    if terms:
                        self.update_terminology_db(terms, f"Student update: {update.progress_text[:50]}...")
                        new_terms += len([t for tlist in terms.values() for t in tlist])
            
            # Analyze faculty updates
            faculty_updates = db.query(FacultyUpdate).filter(
                FacultyUpdate.created_at >= recent_date
            ).all()
            
            for update in faculty_updates:
                combined_text = f"{update.announcements_text or ''} {update.projects_text or ''}"
                
                if combined_text.strip():
                    terms = self.extract_terminology(combined_text)
                    if terms:
                        self.update_terminology_db(terms, f"Faculty update: {update.announcements_text[:50]}...")
                        new_terms += len([t for tlist in terms.values() for t in tlist])
        
        # Get top terms for summary
        with sqlite3.connect(self.db_path) as conn:
            top_terms = conn.execute('''
                SELECT term, frequency FROM terminology 
                WHERE confidence_score > 0.4
                ORDER BY frequency DESC LIMIT 20
            ''').fetchall()
        
        # Save snapshot
        snapshot = KnowledgeSnapshot(
            timestamp=snapshot_time,
            total_submissions=len(student_updates) + len(faculty_updates),
            new_terms_found=new_terms,
            updated_terms=updated_terms,
            top_terms=top_terms
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO snapshots 
                (total_submissions, new_terms_found, updated_terms, top_terms)
                VALUES (?, ?, ?, ?)
            ''', (
                snapshot.total_submissions,
                snapshot.new_terms_found, 
                snapshot.updated_terms,
                json.dumps(top_terms)
            ))
        
        return snapshot
    
    def get_domain_vocabulary(self, category: Optional[str] = None, min_confidence: float = 0.5) -> Dict[str, TerminologyEntry]:
        """Get domain vocabulary for AI prompt enhancement"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT term, category, frequency, contexts, first_seen, last_seen, confidence_score, user_approved
                FROM terminology 
                WHERE confidence_score >= ?
            '''
            params = [min_confidence]
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY frequency DESC LIMIT 100'
            
            rows = conn.execute(query, params).fetchall()
            
            vocabulary = {}
            for row in rows:
                term, cat, freq, contexts_json, first_seen, last_seen, conf, approved = row
                contexts = json.loads(contexts_json) if contexts_json else []
                
                vocabulary[term] = TerminologyEntry(
                    term=term,
                    category=cat,
                    frequency=freq,
                    contexts=contexts,
                    first_seen=datetime.fromisoformat(first_seen),
                    last_seen=datetime.fromisoformat(last_seen),
                    confidence_score=conf,
                    user_approved=bool(approved)
                )
            
            return vocabulary
    
    def get_enhanced_prompt_context(self, text_context: str) -> str:
        """Generate enhanced context for AI prompts based on learned vocabulary"""
        vocabulary = self.get_domain_vocabulary(min_confidence=0.6)
        
        # Categorize vocabulary for prompt injection
        medical_terms = [term for term, entry in vocabulary.items() if entry.category == 'medical_terms']
        research_methods = [term for term, entry in vocabulary.items() if entry.category == 'research_methods']
        abbreviations = [term for term, entry in vocabulary.items() if entry.category == 'abbreviations']
        
        context_addition = ""
        
        if medical_terms:
            context_addition += f"\n\nDomain Vocabulary - Medical Terms: {', '.join(medical_terms[:10])}"
        
        if research_methods:
            context_addition += f"\nResearch Methods: {', '.join(research_methods[:10])}"
        
        if abbreviations:
            context_addition += f"\nCommon Abbreviations: {', '.join(abbreviations[:15])}"
        
        # Add writing quality guidelines based on common issues
        common_issues = self.get_common_writing_issues()
        if common_issues:
            context_addition += f"\n\nWatch for: {', '.join(common_issues[:5])}"
        
        return context_addition
    
    def get_common_writing_issues(self) -> List[str]:
        """Get list of common writing issues to watch for"""
        # This could be expanded to track actual issues found in submissions
        return [
            "passive voice overuse",
            "weak qualifier words", 
            "unclear abbreviations",
            "run-on sentences",
            "inconsistent terminology"
        ]
    
    async def approve_term(self, term: str, user_id: int) -> bool:
        """Allow admin users to approve/curate terminology"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute('''
                UPDATE terminology 
                SET user_approved = TRUE, confidence_score = 1.0
                WHERE term = ?
            ''', (term,))
            return result.rowcount > 0
    
    async def reject_term(self, term: str, user_id: int) -> bool:
        """Allow admin users to reject terminology"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute('DELETE FROM terminology WHERE term = ?', (term,))
            return result.rowcount > 0

# Global instance
knowledge_service = KnowledgeBaseService()