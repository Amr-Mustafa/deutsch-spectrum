"""German separable verb detection using dependency parsing."""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class SeparableVerbDetector:
    """Detects and links separable verb parts and reflexive verbs in German text."""

    # Pronominal adverbs that should NOT be treated as separable prefixes
    # These contain prepositions and are handled by VerbPrepositionDetector
    PRONOMINAL_ADVERBS = {
        'daran', 'darauf', 'daraus', 'darin', 'damit', 'danach', 'davon',
        'davor', 'dazu', 'darüber', 'darunter', 'dagegen', 'dafür', 'dabei',
        'woran', 'worauf', 'woraus', 'worin', 'womit', 'wonach', 'wovon',
        'wovor', 'wozu', 'worüber', 'worunter', 'wogegen', 'wofür', 'wobei',
    }

    # Common German separable verb prefixes
    SEPARABLE_PREFIXES = {
        'ab', 'an', 'auf', 'aus', 'bei', 'ein', 'mit',
        'nach', 'vor', 'zu', 'zurück', 'weg', 'her', 'hin',
        # Note: 'da' removed - it's part of pronominal adverbs (damit, daran, etc.)
        'empor', 'entgegen', 'entlang', 'fort', 'gegenüber',
        'heim', 'herab', 'heran', 'herauf', 'heraus', 'herbei',
        'herein', 'herüber', 'herum', 'herunter', 'hervor',
        'hinab', 'hinauf', 'hinaus', 'hinein', 'hinüber',
        'hinunter', 'los', 'nieder', 'voran', 'voraus',
        'vorbei', 'vorüber', 'weiter', 'zusammen',
        'fest'  # festlegen, feststellen, festhalten, festnehmen, etc.
    }

    # Reflexive pronouns in German
    REFLEXIVE_PRONOUNS = {
        'sich', 'mich', 'dich', 'uns', 'euch', 'mir', 'dir'
    }

    def detect_separable_verbs(self, doc, exclude_positions=None) -> List[Dict]:
        """
        Detect separable verb pairs in a spaCy Doc.

        Uses dependency parsing to find verb particles (marked as "svp" - separable verb particle)
        and links them with their corresponding verbs.

        Args:
            doc: spaCy Doc object
            exclude_positions: Set of token positions to exclude (e.g., verb-linked prepositions)

        Returns:
            List of dictionaries containing verb-particle pairs:
            [{'verb': verb_token, 'particle': particle_token, 'lemma': infinitive_form}, ...]
        """
        if exclude_positions is None:
            exclude_positions = set()

        separable_pairs = []

        for token in doc:
            # Skip if this position is a verb-linked preposition
            if token.i in exclude_positions:
                continue

            # spaCy marks separable verb particles with dependency relation "svp"
            if token.dep_ == "svp":
                # Skip pronominal adverbs (they're handled by VerbPrepositionDetector)
                if token.text.lower() in self.PRONOMINAL_ADVERBS:
                    continue

                # The head of the particle is the verb
                verb = token.head

                # Verify that the particle is actually a known separable prefix
                if self._is_separable_prefix(token.text.lower()):
                    # Get the lemma (infinitive form) of the verb
                    # For separable verbs, we want to combine particle + verb lemma
                    lemma = self._construct_infinitive(token.text, verb.lemma_)

                    separable_pairs.append({
                        'verb': verb,
                        'particle': token,
                        'lemma': lemma
                    })

                    logger.debug(
                        f"Found separable verb: {verb.text} ... {token.text} "
                        f"(lemma: {lemma})"
                    )

        # Also check for particles that might be ADP (adpositions) or ADV (adverbs)
        # but actually function as verb particles
        # This catches cases where spaCy mislabels the dependency or POS
        for token in doc:
            # Skip if this position is a verb-linked preposition
            if token.i in exclude_positions:
                continue

            # Skip pronominal adverbs
            if token.text.lower() in self.PRONOMINAL_ADVERBS:
                continue

            if token.pos_ in ["ADP", "ADV"] and self._is_separable_prefix(token.text.lower()):
                # Look for nearby verbs that this could be paired with
                verb = self._find_paired_verb(token, doc)
                if verb and not self._already_paired(verb, token, separable_pairs):
                    lemma = self._construct_infinitive(token.text, verb.lemma_)
                    separable_pairs.append({
                        'verb': verb,
                        'particle': token,
                        'lemma': lemma
                    })
                    logger.debug(
                        f"Found separable verb ({token.pos_}): {verb.text} ... {token.text} "
                        f"(lemma: {lemma})"
                    )

        return separable_pairs

    def detect_reflexive_verbs(self, doc) -> List[Dict]:
        """
        Detect reflexive verb pairs in a spaCy Doc.

        Finds reflexive pronouns (sich, mich, dich, etc.) and links them
        with their corresponding verbs.

        Args:
            doc: spaCy Doc object

        Returns:
            List of dictionaries containing verb-pronoun pairs:
            [{'verb': verb_token, 'pronoun': pronoun_token, 'lemma': infinitive_form}, ...]
        """
        reflexive_pairs = []

        for token in doc:
            # Check if token is a reflexive pronoun
            if token.pos_ == "PRON" and token.text.lower() in self.REFLEXIVE_PRONOUNS:
                # Find the verb this pronoun is attached to
                # Common dependencies: 'expl' (expletive), 'obj' (object), 'dobj' (direct object)
                verb = None

                # First, check if the pronoun's head is a verb
                if token.head.pos_ in ["VERB", "AUX"]:
                    verb = token.head
                else:
                    # Otherwise, look for the closest verb in the sentence
                    verb = self._find_verb_for_pronoun(token)

                if verb:
                    # Construct lemma with 'sich' as the standard reflexive pronoun
                    lemma = f"sich {verb.lemma_}"

                    reflexive_pairs.append({
                        'verb': verb,
                        'pronoun': token,
                        'lemma': lemma
                    })

                    logger.debug(
                        f"Found reflexive verb: {verb.text} {token.text} "
                        f"(lemma: {lemma})"
                    )

        return reflexive_pairs

    def _find_verb_for_pronoun(self, pronoun_token) -> any:
        """
        Find the verb associated with a reflexive pronoun.

        Args:
            pronoun_token: The reflexive pronoun token

        Returns:
            The associated verb token or None
        """
        sentence = pronoun_token.sent

        # Look for verbs in the same sentence
        verbs_in_sentence = [token for token in sentence if token.pos_ in ["VERB", "AUX"]]

        if not verbs_in_sentence:
            return None

        # Prefer the closest verb (usually the main verb of the clause)
        closest_verb = min(
            verbs_in_sentence,
            key=lambda v: abs(v.i - pronoun_token.i)
        )

        return closest_verb

    def _is_separable_prefix(self, text: str) -> bool:
        """Check if text is a known separable prefix."""
        return text.lower() in self.SEPARABLE_PREFIXES

    def _construct_infinitive(self, particle: str, verb_lemma: str) -> str:
        """
        Construct the infinitive form of a separable verb.

        Args:
            particle: The separable particle (e.g., "auf")
            verb_lemma: The lemma of the verb (e.g., "stehen")

        Returns:
            The infinitive form (e.g., "aufstehen")
        """
        # Simple concatenation works for most cases
        # The verb lemma is already in infinitive form
        return f"{particle.lower()}{verb_lemma}"

    def _find_paired_verb(self, particle_token, doc) -> any:
        """
        Find the verb that pairs with a particle.

        Uses heuristics:
        1. Look for verb in the same sentence
        2. Prefer verbs that are syntactically close
        3. Check if the verb's lemma could form a valid separable verb with this particle
        4. Exclude cases where the particle is followed by a noun phrase (preposition)

        Args:
            particle_token: The potential particle token
            doc: spaCy Doc object

        Returns:
            The paired verb token or None
        """
        # Check if this looks like a preposition governing a noun phrase
        # If the next token is a determiner, pronoun, or noun, this is likely a preposition
        if particle_token.i + 1 < len(doc):
            next_token = doc[particle_token.i + 1]
            if next_token.pos_ in ["DET", "PRON", "NOUN", "PROPN"]:
                # This looks like a preposition (e.g., "auf das Haus")
                # Not a separable verb particle
                return None

        sentence = particle_token.sent

        # Look for verbs in the same sentence
        verbs_in_sentence = [token for token in sentence if token.pos_ == "VERB" or token.pos_ == "AUX"]

        if not verbs_in_sentence:
            return None

        # Prefer the closest verb
        closest_verb = min(
            verbs_in_sentence,
            key=lambda v: abs(v.i - particle_token.i)
        )

        # Additional validation: check if this could be a valid separable verb
        # by seeing if the particle is commonly used with this type of verb
        return closest_verb

    def _already_paired(self, verb_token, particle_token, existing_pairs: List[Dict]) -> bool:
        """Check if a verb-particle pair already exists in the list."""
        for pair in existing_pairs:
            if pair['verb'].i == verb_token.i and pair['particle'].i == particle_token.i:
                return True
        return False
