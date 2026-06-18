import requests
import json
import re
import sys
from datetime import datetime


def extract_tournament_id(url):
    match = re.search(r"/tournaments/(\d+)", url)
    if match:
        return match.group(1)
    
    if "/t/" in url:
        try:
            html = requests.get(url, timeout=10).text
            match = re.search(r'"shortlink":\{.*?"resourceId":"(\d+)"', html)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"Error fetching short URL: {e}", file=sys.stderr)
    
    raise ValueError(f"Could not extract tournament ID from URL: {url}")


def filter_match_data(match):
    filtered = {
        "id": match.get("id"),
        "roundNum": match.get("roundNum"),
        "state": match.get("state"),
    }
    
    if "entrantA" in match and match["entrantA"]:
        entrant_a = match["entrantA"]
        filtered["entrantA"] = {
            "entrantId": entrant_a.get("entrantId"),
            "score": entrant_a.get("score")
        }
    else:
        filtered["entrantA"] = None
    
    if "entrantB" in match and match["entrantB"]:
        entrant_b = match["entrantB"]
        filtered["entrantB"] = {
            "entrantId": entrant_b.get("entrantId"),
            "score": entrant_b.get("score")
        }
    else:
        filtered["entrantB"] = None
    
    return filtered


def filter_bracket_data(bracket_data):
    bracket_body = bracket_data.get("body", [])
    
    if isinstance(bracket_body, list) and bracket_body:
        bracket = bracket_body[0]
    else:
        bracket = bracket_body
    
    filtered = {
        "id": bracket.get("id"),
        "config": {
            "bracketType": bracket.get("config", {}).get("bracketType"),
            "consolationMatch": bracket.get("config", {}).get("consolationMatch"),
            "matchBestOfPerRound": bracket.get("config", {}).get("matchBestOfPerRound")
        },
        "entrants": [
            {
                "id": e.get("id"),
                "name": e.get("name"),
                "team": {
                    "members": [
                        {"displayName": m.get("displayName")}
                        for m in e.get("team", {}).get("members", [])
                    ]
                }
            }
            for e in bracket.get("entrants", [])
        ],
        "matches": [
            filter_match_data(m)
            for m in bracket.get("matches", [])
        ]
    }
    
    return filtered


def fetch_bracket_data(url):
    tournament_id = extract_tournament_id(url)
    
    print(f"Tournament ID: {tournament_id}")
    
    bracket_url = f"https://api.matcherino.com/__api/brackets?bountyId={tournament_id}&id=0&isAdmin=false"
    print(f"GET: {bracket_url}")
    bracket_response = requests.get(bracket_url, timeout=10)
    bracket_response.raise_for_status()
    raw_data = bracket_response.json()
    
    filtered_data = filter_bracket_data(raw_data)
    
    return {
        "tournament_id": tournament_id,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "bracket": filtered_data
    }


def save_to_file(data, filename=None):
    if filename is None:
        filename = f"bracket_{data['tournament_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename


def print_summary(data):
    bracket = data.get("bracket", {})
    
    print("\n" + "=" * 60)
    print("BRACKET SUMMARY")
    print("=" * 60)
    print(f"Tournament ID: {data['tournament_id']}")
    print(f"Bracket ID: {bracket.get('id', 'N/A')}")
    
    config = bracket.get('config', {})
    entrants = bracket.get('entrants', [])
    matches = bracket.get('matches', [])
    
    print(f"\nConfig:")
    print(f"  Type: {config.get('bracketType', 'N/A')}")
    print(f"  Consolation Match: {config.get('consolationMatch', False)}")
    print(f"  Best of per round: {config.get('matchBestOfPerRound', {})}")
    
    print(f"\nEntrants: {len(entrants)}")
    if entrants:
        print("  First 5 entrants:")
        for i, entrant in enumerate(entrants[:5]):
            members = entrant.get('team', {}).get('members', [])
            member_names = ', '.join([m.get('displayName', 'N/A') for m in members])
            print(f"    {i+1}. {entrant.get('name', 'N/A')} [{member_names}]")
        if len(entrants) > 5:
            print(f"    ... and {len(entrants) - 5} more")
    
    print(f"\nMatches: {len(matches)}")
    if matches:
        print("  First 5 matches (filtered):")
        for i, match in enumerate(matches[:5]):
            a_id = match.get('entrantA', {}).get('entrantId', 'N/A') if match.get('entrantA') else 'N/A'
            b_id = match.get('entrantB', {}).get('entrantId', 'N/A') if match.get('entrantB') else 'N/A'
            a_score = match.get('entrantA', {}).get('score', 'N/A') if match.get('entrantA') else 'N/A'
            b_score = match.get('entrantB', {}).get('score', 'N/A') if match.get('entrantB') else 'N/A'
            print(f"    {i+1}. Round {match.get('roundNum', 'N/A')}: {a_id} ({a_score}) vs ({b_score}) {b_id}")
        if len(matches) > 5:
            print(f"    ... and {len(matches) - 5} more")
    
    print("=" * 60)


def main():
    print("=" * 60)
    print("Matcherino Bracket API Debug Tool (Filtered)")
    print("=" * 60)
    
    url = input("\nEnter Matcherino URL: ").strip()
    if not url:
        print("Error: URL cannot be empty")
        sys.exit(1)
    
    try:
        print("\n" + "-" * 60)
        print("Fetching and filtering bracket data...")
        print("-" * 60)
        
        data = fetch_bracket_data(url)
        
        print_summary(data)
        
        filename = save_to_file(data)
        print(f"\n✅ Filtered bracket data saved to: {filename}")
        
        show_full = input("\nShow filtered JSON in console? (y/N): ").strip().lower()
        if show_full == 'y':
            print("\n" + "=" * 60)
            print("FILTERED BRACKET DATA")
            print("=" * 60)
            print(json.dumps(data["bracket"], indent=2, ensure_ascii=False))
        
        print("\n✅ Done!")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Status code: {e.response.status_code}")
            try:
                print(f"Response: {e.response.text[:500]}")
            except:
                pass
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON response: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
