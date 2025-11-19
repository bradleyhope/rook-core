"""
Deep analysis of Invisible Cities by Italo Calvino
Extract themes, structure, key passages for ROOK's foundational memory
"""

with open('/home/ubuntu/rook-core/invisible_cities_full.txt', 'r', encoding='utf-8') as f:
    full_text = f.read()

# The book is structured as Marco Polo describing cities to Kublai Khan
# Cities are organized into 11 thematic categories

# Let me read key sections and extract themes
analysis = {
    'structure': '',
    'key_themes': [],
    'memorable_cities': [],
    'philosophical_insights': [],
    'key_passages': []
}

# Extract the opening frame
opening_start = full_text.find("Kublai Khan ekes not necessarily")
opening_end = full_text.find("Leaving there and proceeding")
if opening_start != -1 and opening_end != -1:
    opening = full_text[opening_start:opening_end].strip()
    analysis['key_passages'].append({
        'title': 'Opening Frame - Kublai Khan and Marco Polo',
        'text': opening,
        'significance': 'Establishes the relationship between emperor and storyteller, the search for pattern amid decay'
    })

# Find key philosophical passages
# Look for passages about memory, desire, signs, eyes, names, etc.

# Save for manual deep reading
with open('/home/ubuntu/rook-core/invisible_cities_analysis.md', 'w') as f:
    f.write("# Deep Analysis of Invisible Cities\n\n")
    f.write("## Structure\n\n")
    f.write("Marco Polo describes 55 imaginary cities to Kublai Khan.\n")
    f.write("Cities are organized into 11 thematic categories:\n\n")
    f.write("1. Cities and memory\n")
    f.write("2. Cities and desire\n")
    f.write("3. Cities and signs\n")
    f.write("4. Thin cities\n")
    f.write("5. Trading cities\n")
    f.write("6. Cities and eyes\n")
    f.write("7. Cities and names\n")
    f.write("8. Cities and the dead\n")
    f.write("9. Cities and the sky\n")
    f.write("10. Continuous cities\n")
    f.write("11. Hidden cities\n\n")
    
    f.write("## Opening Passage\n\n")
    f.write(opening + "\n\n")
    
    f.write("## Key Themes to Extract\n\n")
    f.write("- Memory and how cities contain their past\n")
    f.write("- Desire and how it shapes perception\n")
    f.write("- Signs and symbols - how meaning is constructed\n")
    f.write("- The invisible within the visible\n")
    f.write("- Pattern recognition amid chaos\n")
    f.write("- The relationship between description and truth\n")
    f.write("- Imagination as a way of knowing\n\n")

print("Analysis started. Now reading full text manually...")
print(f"\nOpening passage extracted ({len(opening)} chars)")
print("\nKey opening insight:")
print(opening[:500] + "...")
