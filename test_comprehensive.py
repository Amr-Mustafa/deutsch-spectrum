"""Comprehensive test of verb-preposition detection."""
import requests
import json

API_URL = "http://localhost:8000/api/v1/analyze"

# Read test sentences
with open('test_wikipedia.txt', 'r', encoding='utf-8') as f:
    sentences = [line.strip() for line in f if line.strip()]

print("=" * 100)
print("COMPREHENSIVE VERB-PREPOSITION TEST")
print("=" * 100)

issues_found = []
total_verbs = 0
verbs_with_preps = 0

for i, sentence in enumerate(sentences, 1):
    print(f"\n[{i}/{len(sentences)}] {sentence}")

    try:
        response = requests.post(API_URL, json={
            'text': sentence,
            'target_word': sentence.split()[0]  # Just to trigger analysis
        })

        if response.ok:
            data = response.json()

            # Find all verbs
            verbs = [t for t in data['tokens'] if t['pos'] in ['VERB', 'AUX']]
            total_verbs += len(verbs)

            for verb in verbs:
                verb_text = verb['text']
                verb_lemma = verb['lemma']

                # Check for verb prepositions
                if verb.get('verb_prepositions'):
                    verbs_with_preps += 1
                    preps = verb['verb_prepositions']
                    prep_str = ', '.join([f"{p['text']}+{p['case']}" for p in preps])

                    # Show analysis
                    separable = " [SEPARABLE]" if verb.get('is_separable') else ""
                    reflexive = " [REFLEXIVE]" if verb.get('is_reflexive') else ""
                    print(f"  ✓ {verb_text} ({verb_lemma}){separable}{reflexive} → {prep_str}")
                else:
                    # Verb without detected prepositions
                    if verb.get('is_separable') or verb.get('is_reflexive'):
                        sep = " [SEP]" if verb.get('is_separable') else ""
                        refl = " [REFL]" if verb.get('is_reflexive') else ""
                        print(f"    {verb_text} ({verb_lemma}){sep}{refl}")
        else:
            print(f"  ✗ API error: {response.status_code}")
            issues_found.append((sentence, f"API error {response.status_code}"))

    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        issues_found.append((sentence, str(e)))

print("\n" + "=" * 100)
print(f"SUMMARY:")
print(f"  Total sentences: {len(sentences)}")
print(f"  Total verbs: {total_verbs}")
print(f"  Verbs with prepositions: {verbs_with_preps} ({verbs_with_preps*100//total_verbs if total_verbs > 0 else 0}%)")
print(f"  Issues found: {len(issues_found)}")
print("=" * 100)
