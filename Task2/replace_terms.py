import json
import re
from pathlib import Path


class TermReplacer:
    def __init__(self, terms_map_file='terms_map.json'):
        self.load_terms_map(terms_map_file)

    def load_terms_map(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.metadata = data.get('metadata', {})
        self.mappings = data.get('mappings', {})

        self.sorted_terms = sorted(self.mappings.items(),
                                   key=lambda x: len(x[0]),
                                   reverse=True)

        print(f"Loaded {len(self.mappings)} term mappings")
        print(f"Source: {self.metadata.get('source_universe', 'Unknown')}")
        print(f"Target: {self.metadata.get('target_universe', 'Unknown')}\n")

    def replace_in_text(self, text):
        result = text
        replacements_made = {}

        for original, replacement in self.sorted_terms:
            count = result.count(original)

            if count > 0:
                pattern = r'\b' + re.escape(original) + r'\b'
                result = re.sub(pattern, replacement, result)
                replacements_made[original] = count

        return result, replacements_made

    def process_file(self, input_path, output_path):
        print(f"Processing: {input_path.name}")

        with open(input_path, 'r', encoding='utf-8') as f:
            original_text = f.read()

        transformed_text, replacements = self.replace_in_text(original_text)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transformed_text)

        print(f"  Saved to: {output_path.name}")
        print(f"  Replacements: {sum(replacements.values())} changes across {len(replacements)} unique terms")

        if replacements:
            top_replacements = sorted(replacements.items(),
                                     key=lambda x: x[1],
                                     reverse=True)[:5]
            for term, count in top_replacements:
                print(f"    - '{term}' → '{self.mappings[term]}' ({count}x)")

        return replacements

    def process_directory(self, input_dir='raw_data', output_dir='knowledge_base'):
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        output_path.mkdir(exist_ok=True)

        text_files = list(input_path.glob('*.txt'))

        if not text_files:
            print(f"No .txt files found in {input_dir}")
            return

        print(f"Found {len(text_files)} files to process\n")
        print("="*60)

        total_replacements = {}

        for i, file_path in enumerate(text_files, 1):
            print(f"\n[{i}/{len(text_files)}]")

            output_file = output_path / file_path.name
            replacements = self.process_file(file_path, output_file)

            for term, count in replacements.items():
                total_replacements[term] = total_replacements.get(term, 0) + count

        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"  Files processed: {len(text_files)}")
        print(f"  Output directory: {output_dir}/")
        print(f"  Total replacements: {sum(total_replacements.values())}")
        print(f"  Unique terms replaced: {len(total_replacements)}")

        return total_replacements


def main():
    print("Star Wars → Fictional Universe Term Replacer")
    print("="*60)
    print()

    if not Path('terms_map.json').exists():
        print("Error: terms_map.json not found!")
        print("Please run generate_terms_map.py first")
        return

    if not Path('raw_data').exists():
        print("Error: raw_data/ directory not found!")
        print("Please run scraper.py first to download articles")
        return

    replacer = TermReplacer('terms_map.json')

    replacer.process_directory('raw_data', 'knowledge_base')

    print("\nYour unique knowledge base is ready!")
    print("  Location: knowledge_base/")
    print("  The LLM has never seen this fictional universe before.")


if __name__ == "__main__":
    main()
