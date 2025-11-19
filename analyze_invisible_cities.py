import re

# Read the full text
with open('/home/ubuntu/rook-core/invisible_cities_full.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract city descriptions and themes
cities = []
current_city = None
current_text = []

lines = text.split('\n')
for i, line in enumerate(lines):
    # Look for city introductions (usually start with capital letter after blank lines)
    if line.strip() and len(line.strip()) > 20 and not line.strip().startswith('Cities'):
        if any(keyword in line for keyword in ['city', 'City', 'arrives', 'reach', 'comes to']):
            if current_city and current_text:
                cities.append({
                    'name': current_city,
                    'text': '\n'.join(current_text)
                })
            # Try to extract city name
            words = line.split()
            for word in words:
                if word[0].isupper() and len(word) > 3 and word not in ['Marco', 'Kublai', 'Khan', 'Polo']:
                    current_city = word.strip(',.')
                    break
            current_text = [line]
        elif current_city:
            current_text.append(line)

# Add last city
if current_city and current_text:
    cities.append({
        'name': current_city,
        'text': '\n'.join(current_text)
    })

print(f"Found {len(cities)} city descriptions")
print("\nFirst 10 cities:")
for i, city in enumerate(cities[:10]):
    print(f"{i+1}. {city['name']}: {len(city['text'])} chars")
    print(f"   Preview: {city['text'][:100]}...")
    print()

# Save cities to file
with open('/home/ubuntu/rook-core/invisible_cities_extracted.txt', 'w', encoding='utf-8') as f:
    for city in cities:
        f.write(f"\n{'='*80}\n")
        f.write(f"CITY: {city['name']}\n")
        f.write(f"{'='*80}\n")
        f.write(city['text'])
        f.write('\n\n')

print(f"\nExtracted cities saved to invisible_cities_extracted.txt")
