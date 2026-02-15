"""German verb-preposition combinations with their grammatical cases.

This module contains mappings of German verbs to their common prepositions
and the grammatical case (Akkusativ, Dativ, Genitiv) that the preposition governs.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class VerbPrepositionDetector:
    """Detects verb-preposition combinations and their grammatical cases."""

    # Pronominal adverbs (Pronominaladverbien) that contain prepositions
    # These are compounds like "damit" (da+mit), "darauf" (da+auf), etc.
    PRONOMINAL_ADVERBS = {
        'daran': 'an',
        'darauf': 'auf',
        'daraus': 'aus',
        'darin': 'in',
        'damit': 'mit',
        'danach': 'nach',
        'davon': 'von',
        'davor': 'vor',
        'dazu': 'zu',
        'darüber': 'über',
        'darunter': 'unter',
        'dagegen': 'gegen',
        'dafür': 'für',
        'dabei': 'bei',
        # Also wo- forms (used in questions)
        'woran': 'an',
        'worauf': 'auf',
        'woraus': 'aus',
        'worin': 'in',
        'womit': 'mit',
        'wonach': 'nach',
        'wovon': 'von',
        'wovor': 'vor',
        'wozu': 'zu',
        'worüber': 'über',
        'worunter': 'unter',
        'wogegen': 'gegen',
        'wofür': 'für',
        'wobei': 'bei',
    }

    # Comprehensive mapping of verb lemmas to their common prepositions and cases
    # Format: verb_lemma -> [(preposition, case)]
    VERB_PREPOSITION_MAP = {
        # A
        'achten': [('auf', 'Akkusativ')],
        'anfangen': [('mit', 'Dativ')],
        'ankommen': [('auf', 'Akkusativ'), ('in', 'Dativ')],
        'antworten': [('auf', 'Akkusativ')],
        'arbeiten': [('an', 'Dativ'), ('bei', 'Dativ'), ('für', 'Akkusativ')],
        'sich ärgern': [('über', 'Akkusativ')],
        'aufhören': [('mit', 'Dativ')],
        'aufpassen': [('auf', 'Akkusativ')],
        'sich aufregen': [('über', 'Akkusativ')],

        # B
        'sich bedanken': [('bei', 'Dativ'), ('für', 'Akkusativ')],
        'sich beeilen': [('mit', 'Dativ')],
        'beginnen': [('mit', 'Dativ')],
        'beitragen': [('zu', 'Dativ')],
        'sich beklagen': [('über', 'Akkusativ'), ('bei', 'Dativ')],
        'sich bemühen': [('um', 'Akkusativ')],
        'berichten': [('über', 'Akkusativ'), ('von', 'Dativ')],
        'sich beschäftigen': [('mit', 'Dativ')],
        'sich beschweren': [('über', 'Akkusativ'), ('bei', 'Dativ')],
        'bestehen': [('aus', 'Dativ'), ('auf', 'Dativ')],
        'sich bewerben': [('um', 'Akkusativ'), ('bei', 'Dativ')],
        'sich beziehen': [('auf', 'Akkusativ')],
        'bitten': [('um', 'Akkusativ')],

        # D
        'danken': [('für', 'Akkusativ')],
        'denken': [('an', 'Akkusativ'), ('über', 'Akkusativ')],
        'diskutieren': [('über', 'Akkusativ')],

        # E
        'sich eignen': [('für', 'Akkusativ')],
        'sich entscheiden': [('für', 'Akkusativ'), ('gegen', 'Akkusativ')],
        'sich entschuldigen': [('bei', 'Dativ'), ('für', 'Akkusativ')],
        'sich erinnern': [('an', 'Akkusativ')],
        'sich erkundigen': [('nach', 'Dativ')],
        'erzählen': [('von', 'Dativ'), ('über', 'Akkusativ')],

        # F
        'fragen': [('nach', 'Dativ')],
        'sich freuen': [('auf', 'Akkusativ'), ('über', 'Akkusativ')],
        'sich fürchten': [('vor', 'Dativ')],

        # G
        'gehören': [('zu', 'Dativ')],
        'sich gewöhnen': [('an', 'Akkusativ')],
        'glauben': [('an', 'Akkusativ')],
        'gratulieren': [('zu', 'Dativ')],

        # H
        'halten': [('für', 'Akkusativ'), ('von', 'Dativ')],
        'sich handeln': [('um', 'Akkusativ')],
        'helfen': [('bei', 'Dativ')],
        'hoffen': [('auf', 'Akkusativ')],

        # I
        'sich interessieren': [('für', 'Akkusativ')],
        'sich irren': [('in', 'Dativ')],

        # K
        'kämpfen': [('für', 'Akkusativ'), ('gegen', 'Akkusativ'), ('um', 'Akkusativ')],
        'sich konzentrieren': [('auf', 'Akkusativ')],
        'sich kümmern': [('um', 'Akkusativ')],

        # L
        'lachen': [('über', 'Akkusativ')],
        'leiden': [('an', 'Dativ'), ('unter', 'Dativ')],

        # N
        'nachdenken': [('über', 'Akkusativ')],

        # R
        'rechnen': [('mit', 'Dativ')],
        'reden': [('über', 'Akkusativ'), ('von', 'Dativ'), ('mit', 'Dativ')],

        # S
        'sich schämen': [('für', 'Akkusativ')],
        'schreiben': [('an', 'Akkusativ'), ('über', 'Akkusativ')],
        'sich sehnen': [('nach', 'Dativ')],
        'sorgen': [('für', 'Akkusativ')],
        'sich sorgen': [('um', 'Akkusativ')],
        'sprechen': [('über', 'Akkusativ'), ('von', 'Dativ'), ('mit', 'Dativ')],
        'sterben': [('an', 'Dativ')],
        'suchen': [('nach', 'Dativ')],

        # T
        'teilnehmen': [('an', 'Dativ')],
        'sich treffen': [('mit', 'Dativ')],
        'träumen': [('von', 'Dativ')],

        # U
        'sich unterhalten': [('über', 'Akkusativ'), ('mit', 'Dativ')],

        # V
        'sich verabschieden': [('von', 'Dativ')],
        'sich verlassen': [('auf', 'Akkusativ')],
        'sich verlieben': [('in', 'Akkusativ')],
        'verzichten': [('auf', 'Akkusativ')],
        'sich vorbereiten': [('auf', 'Akkusativ')],

        # W
        'warten': [('auf', 'Akkusativ')],
        'sich wenden': [('an', 'Akkusativ')],
        'sich wundern': [('über', 'Akkusativ')],

        # Z
        'zweifeln': [('an', 'Dativ')],
    }

    # General preposition case rules (when preposition is NOT in specific verb combination)
    # Some prepositions can take different cases depending on context
    PREPOSITION_CASES = {
        # Two-way prepositions (Wechselpräpositionen) - can be Akkusativ or Dativ
        'an': 'Akkusativ/Dativ',
        'auf': 'Akkusativ/Dativ',
        'hinter': 'Akkusativ/Dativ',
        'in': 'Akkusativ/Dativ',
        'neben': 'Akkusativ/Dativ',
        'über': 'Akkusativ/Dativ',
        'unter': 'Akkusativ/Dativ',
        'vor': 'Akkusativ/Dativ',
        'zwischen': 'Akkusativ/Dativ',

        # Akkusativ prepositions
        'bis': 'Akkusativ',
        'durch': 'Akkusativ',
        'für': 'Akkusativ',
        'gegen': 'Akkusativ',
        'ohne': 'Akkusativ',
        'um': 'Akkusativ',

        # Dativ prepositions
        'aus': 'Dativ',
        'bei': 'Dativ',
        'mit': 'Dativ',
        'nach': 'Dativ',
        'seit': 'Dativ',
        'von': 'Dativ',
        'zu': 'Dativ',

        # Genitiv prepositions (less common)
        'während': 'Genitiv',
        'wegen': 'Genitiv',
        'trotz': 'Genitiv',
        'statt': 'Genitiv',
        'anstatt': 'Genitiv',
    }

    def detect_verb_prepositions(self, doc, verb_token, verb_lemma=None) -> List[Dict]:
        """
        Detect prepositions associated with a verb using dependency parsing.

        This method uses a dynamic approach based on syntactic relationships
        rather than a fixed verb-preposition dictionary, making it scalable
        to any German verb.

        Args:
            doc: spaCy Doc object
            verb_token: The verb token to analyze
            verb_lemma: Optional override for the verb's lemma (useful for separable verbs)

        Returns:
            List of dictionaries with preposition information:
            [{'preposition': token, 'case': 'Akkusativ/Dativ', 'position': int}, ...]
        """
        results = []

        # Get the verb lemma for optional dictionary lookup
        # Use provided lemma if available (important for separable verbs like "beitragen")
        if verb_lemma is None:
            verb_lemma = verb_token.lemma_

        # Check if this is a reflexive verb (lemma starts with "sich")
        if verb_lemma.startswith('sich '):
            # Use the full reflexive lemma for lookup
            lookup_lemma = verb_lemma
        else:
            lookup_lemma = verb_lemma

        # Get expected prepositions for this verb (optional, for specific case info)
        # This is now optional - we primarily use dependency parsing
        expected_preps = self.VERB_PREPOSITION_MAP.get(lookup_lemma, [])

        # Look for prepositions near the verb (within the same clause)
        sentence = verb_token.sent

        for token in sentence:
            prep_text = None
            actual_token = token  # The token to highlight

            # Check if this is a preposition (ADP = adposition)
            if token.pos_ == 'ADP':
                prep_text = token.text.lower()

            # Check if this is a pronominal adverb (damit, darauf, etc.)
            elif token.pos_ == 'ADV' and token.text.lower() in self.PRONOMINAL_ADVERBS:
                # Extract the preposition from the pronominal adverb
                prep_text = self.PRONOMINAL_ADVERBS[token.text.lower()]
                logger.debug(f"Found pronominal adverb: {token.text} -> {prep_text}")

            # If we found a preposition (either direct or from pronominal adverb)
            if prep_text:
                # If we have dictionary data for this verb, use it to filter
                # This ensures we only report prepositions that are known to go with this verb
                if expected_preps:
                    # Check if this preposition is in the verb's expected list
                    if not any(prep == prep_text for prep, _ in expected_preps):
                        # This preposition is not expected for this verb
                        # Skip it (it's likely an adjunct, not a verb argument)
                        continue

                # Check if this preposition is syntactically connected to the verb
                if self._is_prep_connected_to_verb(token, verb_token, doc):
                    # Determine the case (pass token for morphological analysis)
                    case = self._determine_case(prep_text, expected_preps, token)

                    results.append({
                        'preposition': actual_token,  # The actual token (could be "damit", "auf", etc.)
                        'case': case,
                        'position': actual_token.idx
                    })

                    logger.debug(
                        f"Found verb-preposition: {verb_lemma} + {prep_text} ({case})"
                    )

        return results

    def _is_prep_connected_to_verb(self, prep_token, verb_token, doc) -> bool:
        """
        Check if a preposition is syntactically connected to a verb.

        Uses dependency parsing to determine if the preposition is part of
        the verb's argument structure (not just a nearby modifier).

        Only returns True for prepositions that are true verb complements,
        not optional adjuncts.
        """
        # Check if preposition is in the same sentence
        if prep_token.sent != verb_token.sent:
            return False

        # Strategy 1: Check if the prepositional phrase is a direct argument
        # Look at the object of the preposition and check its relationship to the verb
        for child in prep_token.children:
            if child.head == prep_token:  # child depends on the preposition
                # Check if this child (the prepositional object) has a dependency to the verb
                # Common dependencies for verb complements:
                # - "mo" (modifier, but can be argument)
                # - "op" (prepositional object)
                # - "obl" (oblique argument)
                # - "oa" (accusative object)

                # Walk up the dependency tree to find connection to verb
                current = child
                for _ in range(3):  # Max 3 hops up the tree
                    if current.head == verb_token:
                        # The prepositional phrase connects to our verb
                        # Now check if it's an argument (not just adjunct)
                        # Arguments typically have dependencies: obj, obl, op, oa
                        # Adjuncts have: mo (modifier), advmod, etc.

                        # For German, "mo" can be either argument or adjunct
                        # We need to check if this preposition is common with this verb
                        if current.dep_ in ['op', 'oa', 'obl', 'obj', 'mo']:
                            # Additional check: preposition should be marked as "case"
                            # or be an ADP governing the object
                            if prep_token.dep_ == 'case' or prep_token.pos_ == 'ADP':
                                return True
                        return False
                    current = current.head
                    if current == current.head:  # Root of tree
                        break

        # Strategy 2: Check if preposition itself has direct dependency to verb
        # Some parsers connect prepositions directly
        if prep_token.head == verb_token:
            # Verify it's not just a loose adjunct
            # True arguments usually don't have dep "mo" when directly attached
            if prep_token.dep_ in ['op', 'obl', 'obj', 'oa']:
                return True

        # Strategy 3: For pronominal adverbs (damit, darauf), check proximity
        # These are often parsed differently
        if prep_token.text.lower() in self.PRONOMINAL_ADVERBS:
            # Check if it's within reasonable distance and no intervening verbs
            distance = abs(prep_token.i - verb_token.i)
            if distance <= 4:  # Tighter constraint for pronominal adverbs
                tokens_between = doc[min(prep_token.i, verb_token.i):max(prep_token.i, verb_token.i)]
                other_verbs = [t for t in tokens_between if t.pos_ in ['VERB', 'AUX'] and t != verb_token]
                if not other_verbs:
                    # Check if it's directly connected to verb in dependency tree
                    current = prep_token
                    for _ in range(3):
                        if current.head == verb_token:
                            return True
                        current = current.head
                        if current == current.head:
                            break

        return False

    def _determine_case(self, preposition: str, expected_preps: List[tuple], prep_token=None) -> str:
        """
        Determine the grammatical case for a preposition in context.

        Uses multiple strategies:
        1. Analyze the actual case of the prepositional object (most accurate)
        2. Check verb-specific dictionary (optional, for common cases)
        3. Use general preposition rules (fallback)

        Args:
            preposition: The preposition text
            expected_preps: List of expected (prep, case) tuples for this verb
            prep_token: The actual preposition token (for analyzing its object)

        Returns:
            Case string (e.g., "Akkusativ", "Dativ", "Akkusativ/Dativ")
        """
        # Strategy 1: Try to infer case from the prepositional object's morphology
        if prep_token:
            detected_case = self._detect_case_from_object(prep_token)
            if detected_case and detected_case != 'Unknown':
                return detected_case

        # Strategy 2: Check verb-specific dictionary (optional)
        for prep, case in expected_preps:
            if prep == preposition:
                return case

        # Strategy 3: Use general preposition case rules
        return self.PREPOSITION_CASES.get(preposition, 'Unknown')

    def _detect_case_from_object(self, prep_token) -> Optional[str]:
        """
        Detect grammatical case by analyzing the prepositional object.

        Examines the morphological features of the preposition's dependent
        (usually a noun or determiner) to infer the case.

        Args:
            prep_token: The preposition token

        Returns:
            Case string or None if cannot be determined
        """
        # Look for the object of the preposition (usually has dep="pobj" or "nk")
        for child in prep_token.children:
            # Check morphological features for case information
            if child.morph.get('Case'):
                case_values = child.morph.get('Case')
                if case_values:
                    # spaCy uses standard abbreviations: Nom, Acc, Dat, Gen
                    case_map = {
                        'Nom': 'Nominativ',
                        'Acc': 'Akkusativ',
                        'Dat': 'Dativ',
                        'Gen': 'Genitiv'
                    }
                    case_abbrev = case_values[0] if isinstance(case_values, list) else case_values
                    return case_map.get(case_abbrev, None)

        return None
