/**
 * Color mappings for different parts of speech (POS)
 * These colors are used to highlight German words based on their grammatical role
 */

const POS_COLORS = {
  // Universal POS tags (spaCy uses Universal Dependencies)
  'NOUN': '#FFB3BA',       // Light pink - Nouns (Substantive)
  'VERB': '#BAFFC9',       // Light green - Verbs
  'VERB_PARTICLE': '#90EE90', // Lighter green - Separable verb particles
  'ADJ': '#BAE1FF',        // Light blue - Adjectives
  'ADV': '#FFFFBA',        // Light yellow - Adverbs
  'DET': '#E0BBE4',        // Light purple - Determiners (articles)
  'PRON': '#FFDAB9',       // Peach - Pronouns
  'ADP': '#D4A5A5',        // Dusty rose - Adpositions (prepositions)
  'CONJ': '#B5EAD7',       // Mint - Conjunctions
  'CCONJ': '#B5EAD7',      // Coordinating conjunctions
  'SCONJ': '#A8D8EA',      // Subordinating conjunctions
  'NUM': '#FFD9B3',        // Light orange - Numbers
  'PROPN': '#FFABAB',      // Bright pink - Proper nouns
  'AUX': '#C7CEEA',        // Lavender - Auxiliary verbs
  'PART': '#D5AAFF',       // Light violet - Particles
  'INTJ': '#FFE5B4',       // Light peach - Interjections
  'PUNCT': '#E8E8E8',      // Very light gray - Punctuation
  'X': '#CCCCCC'           // Gray - Other/unknown
};

const POS_LABELS = {
  'NOUN': 'Noun (Substantiv)',
  'VERB': 'Verb',
  'VERB_PARTICLE': 'Separable Verb Particle',
  'ADJ': 'Adjective (Adjektiv)',
  'ADV': 'Adverb',
  'DET': 'Determiner (Artikel)',
  'PRON': 'Pronoun (Pronomen)',
  'ADP': 'Preposition (Präposition)',
  'CONJ': 'Conjunction (Konjunktion)',
  'CCONJ': 'Coordinating Conjunction',
  'SCONJ': 'Subordinating Conjunction',
  'NUM': 'Number (Zahl)',
  'PROPN': 'Proper Noun (Eigenname)',
  'AUX': 'Auxiliary Verb (Hilfsverb)',
  'PART': 'Particle (Partikel)',
  'INTJ': 'Interjection (Interjektion)',
  'PUNCT': 'Punctuation',
  'X': 'Other'
};

// Make globally available (no module system in Manifest V3 content scripts)
if (typeof window !== 'undefined') {
  window.POS_COLORS = POS_COLORS;
  window.POS_LABELS = POS_LABELS;
}
