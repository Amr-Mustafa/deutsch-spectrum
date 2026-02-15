"""Core POS analysis using spaCy for German text."""
import spacy
from typing import List, Optional
import logging

from .models import Token, VerbPreposition
from .separable_verbs import SeparableVerbDetector
from .verb_prepositions import VerbPrepositionDetector

logger = logging.getLogger(__name__)


class POSAnalyzer:
    """Analyzes German text and returns POS tags using spaCy."""

    def __init__(self):
        """Initialize the analyzer by loading the spaCy model."""
        try:
            logger.info("Loading spaCy German model...")
            # Use large model for better accuracy (especially for separable verbs)
            # Disable NER for speed (we only need POS tags and dependency parsing)
            # Speed optimizations: small clauses + disabled NER + caching = still fast
            self.nlp = spacy.load("de_core_news_lg", disable=["ner"])
            # Initialize verb detectors
            self.verb_detector = SeparableVerbDetector()
            self.prep_detector = VerbPrepositionDetector()
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("German spaCy model not found. Please run: python -m spacy download de_core_news_lg")
            raise

    def analyze_text(
        self,
        text: str,
        target_word: Optional[str] = None,
        target_position: Optional[int] = None
    ) -> List[Token]:
        """
        Analyze German text and return structured POS data.

        Args:
            text: The German text to analyze
            target_word: The specific word being hovered (optional)
            target_position: Character position of the target word (optional)

        Returns:
            List of Token objects with POS information
        """
        if not text or not text.strip():
            return []

        # Process text with spaCy
        doc = self.nlp(text)

        # Detect verb-preposition combinations FIRST
        # This prevents prepositions from being misidentified as separable particles
        verb_prep_positions = set()  # Track which positions are verb-linked prepositions

        temp_verb_preps = {}
        for token in doc:
            if token.pos_ in ['VERB', 'AUX']:
                preps = self.prep_detector.detect_verb_prepositions(doc, token, token.lemma_)
                if preps:
                    temp_verb_preps[token.i] = preps
                    for prep_info in preps:
                        verb_prep_positions.add(prep_info['preposition'].i)

        # Detect separable verbs (exclude positions that are verb-linked prepositions)
        separable_pairs = self.verb_detector.detect_separable_verbs(doc, verb_prep_positions)

        # Detect reflexive verbs
        reflexive_pairs = self.verb_detector.detect_reflexive_verbs(doc)

        # Create a map of verb positions to their full infinitive forms (for separable/reflexive verbs)
        verb_infinitives = {}  # Maps verb token index to infinitive form
        for pair in separable_pairs:
            verb_infinitives[pair['verb'].i] = pair['lemma']
        for pair in reflexive_pairs:
            verb_infinitives[pair['verb'].i] = pair['lemma']

        # Re-detect verb-preposition combinations with correct infinitive forms
        # (Now that we know the full infinitives for separable/reflexive verbs)
        verb_prep_map = {}  # Maps verb token index to list of preposition info
        prep_verb_map = {}  # Maps preposition position to (verb_position, case)

        for token in doc:
            if token.pos_ in ['VERB', 'AUX']:
                # Use the full infinitive if available (for separable/reflexive verbs)
                verb_lemma = verb_infinitives.get(token.i, token.lemma_)
                preps = self.prep_detector.detect_verb_prepositions(doc, token, verb_lemma)
                if preps:
                    verb_prep_map[token.i] = preps
                    # Also create reverse mapping for preposition tokens
                    for prep_info in preps:
                        prep_verb_map[prep_info['position']] = (token.idx, prep_info['case'])

        # Convert spaCy tokens to our Token model
        tokens = []
        for token in doc:
            # Check if this token is part of a separable verb
            separable_info = self._get_separable_info(token, separable_pairs)

            # Check if this token is part of a reflexive verb
            reflexive_info = self._get_reflexive_info(token, reflexive_pairs)

            # Determine POS tag (use VERB_PARTICLE for separable particles)
            pos_tag = token.pos_
            if separable_info and separable_info.get('is_particle'):
                pos_tag = "VERB_PARTICLE"

            # Get is_separable flag and related info
            is_separable = False
            separable_parts = []
            paired_with = []
            is_reflexive = False
            lemma = token.lemma_

            if separable_info:
                is_separable = separable_info.get('is_separable', False)
                parts = separable_info.get('parts')
                if parts:
                    separable_parts.extend(parts)
                paired_pos = separable_info.get('paired_with')
                if paired_pos is not None:
                    paired_with.append(paired_pos)
                if 'lemma' in separable_info:
                    lemma = separable_info['lemma']

            if reflexive_info:
                is_reflexive = reflexive_info.get('is_reflexive', False)
                if 'lemma' in reflexive_info:
                    # For reflexive + separable, combine lemmas
                    if is_separable:
                        lemma = f"sich {separable_info['lemma']}"
                    else:
                        lemma = reflexive_info['lemma']
                parts = reflexive_info.get('parts')
                if parts:
                    # Add reflexive parts that aren't already in separable_parts
                    for part in parts:
                        if part not in separable_parts:
                            separable_parts.append(part)
                paired_pos = reflexive_info.get('paired_with')
                if paired_pos is not None:
                    paired_with.append(paired_pos)

            # Convert to None if empty
            separable_parts = separable_parts if separable_parts else None
            paired_with = paired_with if paired_with else None

            # Add verb-preposition information
            verb_prepositions = None
            linked_verb = None
            governs_case = None

            # If this is a verb, check if it has prepositions
            if token.i in verb_prep_map:
                verb_prepositions = [
                    VerbPreposition(
                        text=prep_info['preposition'].text,
                        case=prep_info['case'],
                        position=prep_info['position']
                    )
                    for prep_info in verb_prep_map[token.i]
                ]
                # Add preposition positions to paired_with for highlighting
                if paired_with is None:
                    paired_with = []
                for prep_info in verb_prep_map[token.i]:
                    paired_with.append(prep_info['position'])

            # If this is a preposition linked to a verb
            if token.idx in prep_verb_map:
                linked_verb, governs_case = prep_verb_map[token.idx]
                # Add verb position to paired_with for highlighting
                if paired_with is None:
                    paired_with = []
                paired_with.append(linked_verb)

            token_data = Token(
                text=token.text,
                pos=pos_tag,
                lemma=lemma,
                start=token.idx,
                end=token.idx + len(token.text),
                is_separable=is_separable,
                separable_parts=separable_parts,
                paired_with=paired_with,
                is_reflexive=is_reflexive,
                verb_prepositions=verb_prepositions,
                linked_verb=linked_verb,
                governs_case=governs_case
            )
            tokens.append(token_data)

        return tokens

    def _get_separable_info(self, token, separable_pairs: List[dict]) -> Optional[dict]:
        """
        Get separable verb information for a token.

        Args:
            token: spaCy token
            separable_pairs: List of detected separable verb pairs

        Returns:
            Dictionary with separable verb info or None
        """
        for pair in separable_pairs:
            verb_token = pair['verb']
            particle_token = pair['particle']
            lemma = pair['lemma']

            if token.i == verb_token.i:
                # This is the verb part
                return {
                    'is_separable': True,
                    'is_particle': False,
                    'parts': [verb_token.text, particle_token.text],
                    'paired_with': particle_token.idx,
                    'lemma': lemma
                }
            elif token.i == particle_token.i:
                # This is the particle part
                return {
                    'is_separable': True,
                    'is_particle': True,
                    'parts': [verb_token.text, particle_token.text],
                    'paired_with': verb_token.idx,
                    'lemma': lemma
                }

        return None

    def _get_reflexive_info(self, token, reflexive_pairs: List[dict]) -> Optional[dict]:
        """
        Get reflexive verb information for a token.

        Args:
            token: spaCy token
            reflexive_pairs: List of detected reflexive verb pairs

        Returns:
            Dictionary with reflexive verb info or None
        """
        for pair in reflexive_pairs:
            verb_token = pair['verb']
            pronoun_token = pair['pronoun']
            lemma = pair['lemma']

            if token.i == verb_token.i:
                # This is the verb part
                return {
                    'is_reflexive': True,
                    'parts': [verb_token.text, pronoun_token.text],
                    'paired_with': pronoun_token.idx,
                    'lemma': lemma
                }
            elif token.i == pronoun_token.i:
                # This is the pronoun part
                return {
                    'is_reflexive': True,
                    'parts': [verb_token.text, pronoun_token.text],
                    'paired_with': verb_token.idx,
                    'lemma': lemma
                }

        return None

    def get_sentence_context(self, doc, token_index: int, max_chars: int = 300) -> str:
        """
        Extract sentence context around a specific token.

        Args:
            doc: spaCy Doc object
            token_index: Index of the target token
            max_chars: Maximum number of characters to return

        Returns:
            Sentence or paragraph context as string
        """
        if token_index < 0 or token_index >= len(doc):
            return ""

        target_token = doc[token_index]
        sentence = target_token.sent

        # If sentence is short enough, return it
        if len(sentence.text) <= max_chars:
            return sentence.text

        # Otherwise, try to get context around target token
        start = max(0, target_token.idx - max_chars // 2)
        end = min(len(doc.text), target_token.idx + max_chars // 2)

        return doc.text[start:end]
