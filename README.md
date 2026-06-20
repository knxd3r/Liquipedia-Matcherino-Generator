# Liquipedia-Matcherino-Generator

A tool to generate Liquipedia wiki code from Matcherino tournament data.

## Features

- Fetches tournament data from Matcherino API
- Generates complete Liquipedia page code
- Supports single and double elimination brackets
- Handles prize pool distribution
- Extracts participant information
- Generates bracket with match scores
- Social media links integration

## Requirements

- Python 3.6+
- requests library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/knxd3r/Liquipedia-Matcherino-Generator.git
cd path/to/file/Liquipedia-Matcherino-Generator
```

2. Install dependencies:
```bash
pip install requests
```

## Usage

1. Run the script:
```bash
python main.py
```

2. Enter the Matcherino tournament URL when prompted:
```
Input Matcherino link: https://matcherino.com/tournaments/123456
```

3. The generated Liquipedia code will be saved to `liquipedia.txt`

## File Structure

- `main.py` - Main entry point
- `matcherino_api.py` - API interaction and data processing
- `liquipedia_generator.py` - Liquipedia page generation
- `participants_table.txt` - Optional fallback participant data
- `liquipedia.txt` - Generated output file

## Known Issues

### Player Flags
Player flags are not automatically detected. You will need to add them manually in the generated code.

### Important
**Always carefully check the generated code before publishing to Liquipedia.**

## Error Handling

The script handles common errors:
- Invalid URLs
- Missing tournament data
- Network timeouts
- File not found for participants table

If `participants_table.txt` is missing, the script will ask if you want to download it from the repository.

## License

MIT License
