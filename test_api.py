import requests
import json

API_URL = "http://localhost:8000/api/v1/analyze"

test_cases = [
    # Separable verbs
    ("Ich stehe um 7 Uhr auf.", "auf", "Test 1.1: aufstehen"),
    ("Er geht heute Abend aus.", "aus", "Test 1.2: ausgehen"),
    ("Sie kam gestern zurück.", "zurück", "Test 1.3: zurückkommen"),
    ("legte sie als Regionale Grünzüge planerisch fest.", "fest", "Test 1.4: festlegen"),

    # Reflexive verbs
    ("Ich freue mich auf den Urlaub.", "mich", "Test 2.1: sich freuen"),
    ("Er wäscht sich jeden Morgen.", "sich", "Test 2.2: sich waschen"),
    ("Wir erinnern uns gerne an die alte Zeit.", "uns", "Test 2.3: sich erinnern"),
    ("Sie interessiert sich für Kunst.", "sich", "Test 2.4: sich interessieren"),
    ("Du musst dich beeilen.", "dich", "Test 2.5: sich beeilen"),

    # Preposition detection (false positive prevention)
    ("Die Daten beziehen sich auf das Verwaltungsgebiet.", "auf", "Test 3.1: auf as preposition (not separable)"),

    # Verb + preposition combinations
    ("Ich warte auf den Bus.", "warte", "Test 4.1: warten auf + Akkusativ"),
    ("Ich freue mich auf den Urlaub.", "freue", "Test 4.2: sich freuen auf + Akkusativ"),
    ("Er denkt an seine Familie.", "denkt", "Test 4.3: denken an + Akkusativ"),
    ("Sie interessiert sich für Kunst.", "interessiert", "Test 4.4: sich interessieren für + Akkusativ"),
    ("Wir sprechen über das Problem.", "sprechen", "Test 4.5: sprechen über + Akkusativ"),

    # Pronominal adverbs (damit, darauf, etc.)
    ("Sie begannen damit.", "begannen", "Test 5.1: beginnen mit (pronominal adverb 'damit')"),
    ("Ich freue mich darauf.", "freue", "Test 5.2: sich freuen auf (pronominal adverb 'darauf')"),
    ("Er denkt daran.", "denkt", "Test 5.3: denken an (pronominal adverb 'daran')"),
]

print("=" * 80)
print("TESTING GERMAN POS HIGHLIGHTER")
print("=" * 80)

for text, target_word, test_name in test_cases:
    print(f"\n{test_name}")
    print(f"Text: {text}")
    print(f"Target: {target_word}")
    
    try:
        response = requests.post(API_URL, json={
            "text": text,
            "target_word": target_word,
            "target_position": text.index(target_word)
        })
        
        if response.status_code == 200:
            data = response.json()
            
            # Find the target token
            target_token = None
            paired_tokens = []

            for token in data['tokens']:
                if token['text'].lower() == target_word.lower():
                    target_token = token

                    # Find paired tokens if exists (now a list)
                    if token.get('paired_with') is not None:
                        paired_positions = token['paired_with']
                        if not isinstance(paired_positions, list):
                            paired_positions = [paired_positions]  # Backward compatibility

                        for pos in paired_positions:
                            for t in data['tokens']:
                                if t['start'] == pos:
                                    paired_tokens.append(t)
                                    break
                    break
            
            if target_token:
                print(f"  ✓ Token: {target_token['text']}")
                print(f"    POS: {target_token['pos']}")
                print(f"    Lemma: {target_token['lemma']}")
                print(f"    Separable: {target_token.get('is_separable', False)}")
                print(f"    Reflexive: {target_token.get('is_reflexive', False)}")

                # Display verb prepositions if present
                if target_token.get('verb_prepositions'):
                    print(f"    Verb Prepositions:")
                    for prep in target_token['verb_prepositions']:
                        print(f"      • {prep['text']} + {prep['case']}")

                # Display case if this is a preposition
                if target_token.get('governs_case'):
                    print(f"    Governs Case: {target_token['governs_case']}")

                if paired_tokens:
                    print(f"  ✓ Paired with: {', '.join([t['text'] for t in paired_tokens])}")
                    if target_token.get('separable_parts'):
                        print(f"    Parts: {target_token.get('separable_parts', [])}")
                else:
                    # Check if this is expected (e.g., for preposition test)
                    if target_token.get('is_separable') or target_token.get('is_reflexive') or target_token.get('verb_prepositions'):
                        print(f"  ✗ NO PAIRED TOKEN FOUND (Expected pairing!)")
                    else:
                        print(f"  ✓ No pairing (as expected for non-separable/non-reflexive)")
            else:
                print(f"  ✗ TARGET TOKEN NOT FOUND")
        else:
            print(f"  ✗ API ERROR: {response.status_code}")
    except Exception as e:
        print(f"  ✗ EXCEPTION: {str(e)}")

print("\n" + "=" * 80)
