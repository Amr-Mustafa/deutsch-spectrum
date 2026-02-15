/**
 * Highlighter Module
 * Handles applying and removing POS-based color highlights to DOM elements
 */

const Highlighter = {
  // Track current highlights for cleanup
  currentHighlights: [],
  currentContainer: null,
  hideTooltipTimer: null,

  /**
   * Apply highlights to a container based on analysis results
   * @param {Element} container - DOM element containing the text
   * @param {Object} analysis - Analysis results from API
   * @param {string} originalText - The original text that was analyzed
   * @param {string} targetWord - The specific word being hovered
   */
  applyHighlights(container, analysis, originalText, targetWord) {
    if (!analysis || !analysis.tokens || analysis.tokens.length === 0) {
      return;
    }

    // Clear previous highlights from this container
    this.clearHighlights(container);

    // Store current container
    this.currentContainer = container;

    // Get all text content from container
    const containerText = container.textContent;

    // Find where our analyzed text appears in the container
    const analyzedTextPosition = containerText.indexOf(originalText);
    if (analyzedTextPosition === -1) {
      console.warn('Analyzed text not found in container');
      return;
    }

    // Find the target token and any paired tokens (for separable verbs)
    const tokensToHighlight = this.findTokensToHighlight(analysis.tokens, targetWord);

    // Apply highlights only for the target word and its separable parts
    tokensToHighlight.forEach(token => {
      const color = window.POS_COLORS[token.pos] || '#CCCCCC';
      const label = window.POS_LABELS[token.pos] || token.pos;

      // Adjust token positions based on where the analyzed text is in the container
      const absoluteStart = analyzedTextPosition + token.start;
      const absoluteEnd = analyzedTextPosition + token.end;

      this.highlightRange(container, absoluteStart, absoluteEnd, {
        color,
        pos: token.pos,
        lemma: token.lemma,
        label,
        isSeparable: token.is_separable,
        isReflexive: token.is_reflexive,
        verbPrepositions: token.verb_prepositions,
        governsCase: token.governs_case
      });
    });
  },

  /**
   * Find tokens to highlight (target word + any paired parts)
   * @param {Array} tokens - All tokens from analysis
   * @param {string} targetWord - The word being hovered
   * @returns {Array} Tokens to highlight
   */
  findTokensToHighlight(tokens, targetWord) {
    const result = [];

    // Find the target token (case-insensitive match)
    const targetToken = tokens.find(t =>
      t.text.toLowerCase() === targetWord.toLowerCase()
    );

    if (!targetToken) {
      return result;
    }

    // Add the target token
    result.push(targetToken);

    // If it has paired tokens (separable/reflexive parts, verb prepositions), add them
    if (targetToken.paired_with) {
      // paired_with is now an array of positions
      const pairedPositions = Array.isArray(targetToken.paired_with)
        ? targetToken.paired_with
        : [targetToken.paired_with]; // Backward compatibility

      pairedPositions.forEach(pos => {
        const pairedToken = tokens.find(t => t.start === pos);
        if (pairedToken && !result.includes(pairedToken)) {
          result.push(pairedToken);
        }
      });
    }

    return result;
  },

  /**
   * Highlight a specific range of text in a container
   */
  highlightRange(container, start, end, options) {
    try {
      // Create a tree walker to iterate through text nodes
      const walker = document.createTreeWalker(
        container,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );

      let currentOffset = 0;
      let currentNode;

      while ((currentNode = walker.nextNode())) {
        const nodeText = currentNode.textContent;
        const nodeLength = nodeText.length;
        const nodeStart = currentOffset;
        const nodeEnd = currentOffset + nodeLength;

        // Check if this text node contains part of our target range
        if (nodeEnd > start && nodeStart < end) {
          // Calculate the portion of this node to highlight
          const highlightStart = Math.max(0, start - nodeStart);
          const highlightEnd = Math.min(nodeLength, end - nodeStart);

          // Create the highlight
          this.highlightTextNode(currentNode, highlightStart, highlightEnd, options);
        }

        currentOffset = nodeEnd;

        // Stop if we've passed the end of our target range
        if (currentOffset >= end) break;
      }
    } catch (error) {
      console.error('Error highlighting range:', error);
    }
  },

  /**
   * Highlight a portion of a text node
   */
  highlightTextNode(textNode, start, end, options) {
    try {
      const text = textNode.textContent;

      // Skip if already highlighted
      if (textNode.parentElement && textNode.parentElement.classList.contains('german-pos-highlight')) {
        return;
      }

      // Create range for the portion to highlight
      const range = document.createRange();
      range.setStart(textNode, start);
      range.setEnd(textNode, end);

      // Create highlight span
      const highlight = document.createElement('span');
      highlight.className = 'german-pos-highlight';
      highlight.style.backgroundColor = options.color;
      highlight.style.opacity = '0.5';
      highlight.style.borderRadius = '3px';
      highlight.style.padding = '2px 4px';
      highlight.style.transition = 'all 0.2s ease';
      highlight.style.cursor = 'help';
      highlight.setAttribute('data-pos', options.pos);
      highlight.setAttribute('data-lemma', options.lemma);
      highlight.setAttribute('data-label', options.label);
      highlight.setAttribute('data-separable', options.isSeparable ? 'true' : 'false');
      highlight.setAttribute('data-reflexive', options.isReflexive ? 'true' : 'false');
      if (options.verbPrepositions) {
        highlight.setAttribute('data-verb-prepositions', JSON.stringify(options.verbPrepositions));
      }
      if (options.governsCase) {
        highlight.setAttribute('data-governs-case', options.governsCase);
      }

      // Add hover event for instant tooltip
      const boundShowTooltip = this.showTooltip.bind(this);
      const boundHideTooltip = this.hideTooltip.bind(this);
      highlight.addEventListener('mouseenter', boundShowTooltip);
      highlight.addEventListener('mouseleave', boundHideTooltip);
      highlight.addEventListener('mouseleave', this.clearHighlights.bind(this, this.currentContainer));

      // Wrap the range in the highlight span
      try {
        range.surroundContents(highlight);
        this.currentHighlights.push(highlight);
      } catch (e) {
        // If surroundContents fails (e.g., range spans multiple elements),
        // try a different approach
        console.warn('surroundContents failed, using extractContents approach', e);
        const contents = range.extractContents();
        highlight.appendChild(contents);
        range.insertNode(highlight);
        this.currentHighlights.push(highlight);
      }
    } catch (error) {
      console.error('Error highlighting text node:', error);
    }
  },

  /**
   * Clear all highlights from a container
   */
  clearHighlights(container) {
    if (!container) return;

    // Remove all highlight spans
    const highlights = container.querySelectorAll('.german-pos-highlight');
    highlights.forEach(span => {
      // Replace the span with its text content
      const parent = span.parentNode;
      if (parent) {
        // Move all child nodes out of the span
        while (span.firstChild) {
          parent.insertBefore(span.firstChild, span);
        }
        // Remove the span
        parent.removeChild(span);

        // Normalize to merge adjacent text nodes
        parent.normalize();
      }
    });

    // Clear our tracking array
    this.currentHighlights = [];
  },

  /**
   * Clear all highlights from the entire page
   */
  clearAllHighlights() {
    const highlights = document.querySelectorAll('.german-pos-highlight');
    highlights.forEach(span => {
      const parent = span.parentNode;
      if (parent) {
        while (span.firstChild) {
          parent.insertBefore(span.firstChild, span);
        }
        parent.removeChild(span);
        parent.normalize();
      }
    });

    this.currentHighlights = [];
    this.currentContainer = null;
  },

  /**
   * Show instant tooltip on hover
   */
  showTooltip(event) {
    const element = event.target;

    // Cancel any pending hide
    if (this.hideTooltipTimer) {
      clearTimeout(this.hideTooltipTimer);
      this.hideTooltipTimer = null;
    }

    // Remove any existing tooltip
    this.hideTooltipImmediately();

    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'german-pos-tooltip';
    tooltip.id = 'german-pos-tooltip';

    // Get data from element
    const lemma = element.getAttribute('data-lemma');
    const pos = element.getAttribute('data-pos');
    const label = element.getAttribute('data-label');
    const isSeparable = element.getAttribute('data-separable') === 'true';
    const isReflexive = element.getAttribute('data-reflexive') === 'true';
    const verbPrepositions = element.getAttribute('data-verb-prepositions');
    const governsCase = element.getAttribute('data-governs-case');

    // Build tooltip content
    let content = `<div class="tooltip-row"><strong>Lemma:</strong> ${lemma}</div>`;
    content += `<div class="tooltip-row"><strong>Type:</strong> ${label}</div>`;
    if (isSeparable) {
      content += `<div class="tooltip-row"><strong>Separable Verb</strong></div>`;
    }
    if (isReflexive) {
      content += `<div class="tooltip-row"><strong>Reflexive Verb</strong></div>`;
    }
    if (verbPrepositions) {
      // Parse JSON array of prepositions
      try {
        const preps = JSON.parse(verbPrepositions);
        if (preps && preps.length > 0) {
          content += `<div class="tooltip-row"><strong>Prepositions:</strong></div>`;
          preps.forEach(prep => {
            content += `<div class="tooltip-row" style="margin-left: 10px;">• ${prep.text} + ${prep.case}</div>`;
          });
        }
      } catch (e) {
        console.error('Error parsing verb prepositions:', e);
      }
    }
    if (governsCase) {
      content += `<div class="tooltip-row"><strong>Case:</strong> ${governsCase}</div>`;
    }

    tooltip.innerHTML = content;

    // Style tooltip with !important to override any page CSS
    tooltip.style.cssText = `
      position: fixed !important;
      background: rgba(0, 0, 0, 0.9) !important;
      color: white !important;
      padding: 10px 12px !important;
      border-radius: 6px !important;
      font-size: 13px !important;
      line-height: 1.5 !important;
      z-index: 2147483647 !important;
      pointer-events: none !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
      min-width: 150px !important;
      transform: none !important;
      animation: none !important;
      opacity: 1 !important;
      visibility: visible !important;
      display: block !important;
    `;

    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.setProperty('left', rect.left + 'px', 'important');
    tooltip.style.setProperty('top', (rect.bottom + 5) + 'px', 'important');

    document.body.appendChild(tooltip);

    // Adjust if tooltip goes off-screen
    const tooltipRect = tooltip.getBoundingClientRect();
    if (tooltipRect.right > window.innerWidth) {
      tooltip.style.left = (window.innerWidth - tooltipRect.width - 10) + 'px';
    }
    if (tooltipRect.bottom > window.innerHeight) {
      tooltip.style.top = (rect.top - tooltipRect.height - 5) + 'px';
    }
  },

  /**
   * Hide tooltip with delay (called on mouseleave)
   */
  hideTooltip() {
    // Cancel any existing timer
    if (this.hideTooltipTimer) {
      clearTimeout(this.hideTooltipTimer);
    }

    // Delay hiding to prevent flickering
    this.hideTooltipTimer = setTimeout(() => {
      this.hideTooltipImmediately();
      this.hideTooltipTimer = null;
    }, 100); // 100ms delay
  },

  /**
   * Hide tooltip immediately (no delay)
   */
  hideTooltipImmediately() {
    const existing = document.getElementById('german-pos-tooltip');
    if (existing) {
      existing.remove();
    }
  },

  /**
   * Check if an element is already highlighted
   */
  isHighlighted(element) {
    return element && element.classList && element.classList.contains('german-pos-highlight');
  }
};

// Make globally available
if (typeof window !== 'undefined') {
  window.Highlighter = Highlighter;
}
