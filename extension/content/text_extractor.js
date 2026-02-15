/**
 * Text Extraction Module
 * Handles extracting words and sentence context from the DOM
 */

const TextExtractor = {
  /**
   * Extract context around a hovered element
   * @param {Event} event - Mouse event
   * @returns {Object|null} Context object with {text, target_word, target_position}
   */
  extractContext(event) {
    const range = this.getRangeAtPoint(event.clientX, event.clientY);
    if (!range) return null;

    const word = this.getWordAtRange(range);
    if (!word || !this.isGermanWord(word)) return null;

    // Get full sentence for accurate POS tagging (especially for separable verbs)
    const sentence = this.getFullSentence(range);
    if (!sentence) return null;

    // Find word position in sentence
    const position = sentence.indexOf(word);

    return {
      text: sentence,
      target_word: word,
      target_position: position >= 0 ? position : 0
    };
  },

  /**
   * Get range at specific coordinates
   */
  getRangeAtPoint(x, y) {
    if (document.caretRangeFromPoint) {
      return document.caretRangeFromPoint(x, y);
    } else if (document.caretPositionFromPoint) {
      // Firefox
      const position = document.caretPositionFromPoint(x, y);
      if (!position) return null;
      const range = document.createRange();
      range.setStart(position.offsetNode, position.offset);
      range.setEnd(position.offsetNode, position.offset);
      return range;
    }
    return null;
  },

  /**
   * Get word at a specific range
   */
  getWordAtRange(range) {
    const node = range.startContainer;
    if (node.nodeType !== Node.TEXT_NODE) return null;

    const text = node.textContent;
    const offset = range.startOffset;

    // German word pattern: includes umlauts (ä, ö, ü, Ä, Ö, Ü) and ß
    const wordPattern = /[a-zA-ZäöüÄÖÜß]+/g;
    let match;

    while ((match = wordPattern.exec(text)) !== null) {
      const start = match.index;
      const end = match.index + match[0].length;

      if (offset >= start && offset <= end) {
        return match[0];
      }
    }

    return null;
  },

  /**
   * Check if a word is likely German
   * Simple heuristic: check for German-specific characters or common patterns
   */
  isGermanWord(word) {
    if (!word || word.length < 2) return false;

    // Has German-specific characters
    if (/[äöüÄÖÜß]/.test(word)) return true;

    // Common German words/patterns (basic check)
    // Allow most words but filter out very common English-only patterns
    return true; // For now, accept all words (API will handle analysis)
  },

  /**
   * Get the full sentence containing the range (no character limit)
   * @param {Range} range - The range to find the sentence for
   * @returns {string} Complete sentence
   */
  getFullSentence(range) {
    const node = range.startContainer;
    if (!node) return null;

    // Find the containing paragraph or sentence
    let container = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;

    // Walk up the DOM tree to find a suitable text container
    while (container && !this.isTextContainer(container)) {
      container = container.parentElement;
    }

    if (!container) return null;

    // Get all text content from the container
    const fullText = container.textContent;

    // Extract the complete sentence (no char limit)
    const cursorPosition = this.getCursorPositionInContainer(range, container);
    const sentence = this.extractSentence(fullText, cursorPosition, 10000); // Large limit for full sentence

    return sentence || fullText;
  },

  /**
   * Get sentence context around a range
   * @param {Range} range - The range around which to find context
   * @param {number} maxChars - Maximum characters to return
   * @returns {string} Sentence or paragraph context
   */
  getSentenceContext(range, maxChars = 300) {
    const node = range.startContainer;
    if (!node) return null;

    // Find the containing paragraph or sentence
    let container = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;

    // Walk up the DOM tree to find a suitable text container
    while (container && !this.isTextContainer(container)) {
      container = container.parentElement;
    }

    if (!container) return null;

    // Get all text content from the container
    const fullText = container.textContent;

    // Try to extract a sentence around the cursor
    const cursorPosition = this.getCursorPositionInContainer(range, container);
    const sentence = this.extractSentence(fullText, cursorPosition, maxChars);

    return sentence || fullText.substring(0, maxChars);
  },

  /**
   * Check if element is a good text container
   */
  isTextContainer(element) {
    const tag = element.tagName.toLowerCase();
    return ['p', 'div', 'span', 'article', 'section', 'li', 'td', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag);
  },

  /**
   * Get cursor position within a container element
   */
  getCursorPositionInContainer(range, container) {
    const preRange = document.createRange();
    preRange.selectNodeContents(container);
    preRange.setEnd(range.startContainer, range.startOffset);
    return preRange.toString().length;
  },

  /**
   * Extract a sentence around a specific position
   * @param {string} text - Full text
   * @param {number} position - Position in text
   * @param {number} maxChars - Maximum characters
   * @returns {string} Extracted sentence
   */
  extractSentence(text, position, maxChars) {
    // German sentence boundaries: . ! ? (considering that German uses „" for quotes)
    const sentenceEndPattern = /[.!?]+[\s„"'")]*/g;

    let sentenceStart = 0;
    let sentenceEnd = text.length;

    // Find sentence start (work backwards from position)
    for (let i = position - 1; i >= 0; i--) {
      if (/[.!?]/.test(text[i])) {
        sentenceStart = i + 1;
        break;
      }
    }

    // Find sentence end (work forwards from position)
    for (let i = position; i < text.length; i++) {
      if (/[.!?]/.test(text[i])) {
        sentenceEnd = i + 1;
        break;
      }
    }

    // Trim whitespace
    let sentence = text.substring(sentenceStart, sentenceEnd).trim();

    // If sentence is too long, truncate around the position
    if (sentence.length > maxChars) {
      const localPosition = position - sentenceStart;
      const halfMax = Math.floor(maxChars / 2);

      const start = Math.max(0, localPosition - halfMax);
      const end = Math.min(sentence.length, localPosition + halfMax);

      sentence = sentence.substring(start, end).trim();
    }

    return sentence;
  },

  /**
   * Get the containing element for a range
   */
  getContainingElement(range) {
    const node = range.startContainer;
    return node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
  }
};

// Make globally available
if (typeof window !== 'undefined') {
  window.TextExtractor = TextExtractor;
}
