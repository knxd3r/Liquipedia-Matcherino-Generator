import re
import requests


def determine_tier(prizepool):
    if prizepool >= 100000:
        return 1
    elif prizepool >= 10000:
        return 2
    elif prizepool >= 1000:
        return 3
    else:
        return 4


REGION_MAP = {
    6: "|country=north america",
    7: "|country=north america",
    8: "|country=north america",
    9: "|country=north america",
    10: "|country=north america",

    11: "|country=south america",
    12: "|country=south america",
    13: "|country=south america",

    14: """|country=europe
|country2=middle east
|country3=cis
|country4=africa""",

    15: """|country=europe
|country2=middle east
|country3=cis
|country4=africa""",

    17: """|country=europe
|country2=middle east
|country3=cis
|country4=africa""",

    18: """|country=europe
|country2=middle east
|country3=cis
|country4=africa""",

    25: """|country=europe
|country2=middle east
|country3=cis
|country4=africa""",

    20: "|country=asia pacific",
    21: "|country=asia pacific",
    22: "|country=asia pacific",
    23: "|country=asia pacific",
    24: "|country=asia pacific",

    26: "|country=middle east",
}


def extract_id(url):
    if not url.startswith("https://matcherino.com/"):
        raise ValueError("Only Matcherino URLs are allowed")
    
    match = re.search(r"/tournaments/(\d+)", url)
    if match:
        return match.group(1)
    
    if "/t/" in url:
        html = requests.get(url, timeout=10).text
        match = re.search(r'"shortlink":\{.*?"resourceId":"(\d+)"', html)
        if match:
            return match.group(1)
    
    raise ValueError("Cannot define tournament ID.")


def extract_prizepool(balance):
    return round(int(balance) / 100, 2)

def get_rounds_bo(matches, config):
    bo_per_round = config.get("matchBestOfPerRound") or {}
    total_rounds = max(
        (m.get("roundNum", 0) for m in matches),
        default=0
    )
    result = []
    for round_num in range(1, total_rounds + 1):
        stage_size = 2 ** (total_rounds - round_num + 1)
        bo = bo_per_round.get(str(stage_size), 3)
        result.append(bo)

    return result

def get_tournament_data(url):
    tournament_id = extract_id(url)

    info_url = f"https://api.matcherino.com/__api/bounties/findById?id={tournament_id}"
    response = requests.get(info_url, timeout=10)
    response.raise_for_status()
    data = response.json()["body"]

    organizer = data.get("creator", {}).get("displayName", "")

    prizepool = extract_prizepool(data.get("balance", 0))
    tier = determine_tier(prizepool)

    bracket_url = (
        f"https://api.matcherino.com/__api/brackets"
        f"?bountyId={tournament_id}&id=0&isAdmin=false"
    )

    bracket_response = requests.get(bracket_url, timeout=10)
    bracket_response.raise_for_status()
    bracket_body = bracket_response.json()["body"]

    bracket_data = bracket_body[0] if isinstance(bracket_body, list) else bracket_body

    entrants = bracket_data.get("entrants", [])
    matches = bracket_data.get("matches", [])
    config = bracket_data.get("config", {})
    print("\n=== ROUND STATS ===")

    round_counts = {}

    for match in matches:
       r = match.get("roundNum")
       round_counts[r] = round_counts.get(r, 0) + 1

    for r in sorted(round_counts):
       print(f"Round {r}: {round_counts[r]} matches")
       print("\n=== ROUNDS ===")

    entrant_lookup = {}

    for entrant in entrants:
        entrant_lookup[entrant["id"]] = entrant.get("name", "TBD")

    print("\n=== ALL ROUNDS ===")

    for match in matches:
        print(
        "Round:",
        match.get("roundNum"),
        "| ID:",
        match.get("id"),
        "|",
        entrant_lookup.get(
            match.get("entrantA", {}).get("entrantId"),
            "TBD"
        ),
        "vs",
        entrant_lookup.get(
            match.get("entrantB", {}).get("entrantId"),
            "TBD"
        )
    )


    results_matches = []

    allowed_rounds = sorted({m.get("roundNum") for m in matches})[-3:]

    print("ALLOWED:", allowed_rounds)

    for match in matches:

        round_num = match.get("roundNum")

        if round_num not in allowed_rounds:
          continue

        a_id = (match.get("entrantA") or {}).get("entrantId")
        b_id = (match.get("entrantB") or {}).get("entrantId")

        match_copy = match.copy()

        match_copy["entrantA"] = {
            "entrantId": a_id,
            "name": entrant_lookup.get(a_id, "TBD"),
            "score": (match.get("entrantA") or {}).get("score", "")
        }

        match_copy["entrantB"] = {
        "entrantId": b_id,
        "name": entrant_lookup.get(b_id, "TBD"),
        "score": (match.get("entrantB") or {}).get("score", "")
    }

        results_matches.append(match_copy)

    results_matches.sort(
    key=lambda m: (
        m.get("roundNum", 0),
        m.get("id", 0)
    )
)

    total_rounds = max(
    (m.get("totalRounds", 0) for m in matches),
    default=0
)


    third_place_match = None
    gf_match = None
    consolation_matches = []

    max_round = max(m.get("roundNum", 0) for m in matches)

    if config.get("consolationMatch"):
       gf_match = next(
        (m for m in matches if m.get("roundNum") == max_round),
        None
    )

    consolation_matches = [
        m for m in matches
        if m.get("roundNum") == max_round
        and m != gf_match
        and m.get("entrantA")
        and m.get("entrantB")
    ]

    if consolation_matches:
        third_place_match = consolation_matches[0]

    third_place_match = (
    consolation_matches[0]
    if consolation_matches
    else None
)

    for match in consolation_matches:
          a_id = (match.get("entrantA") or {}).get("entrantId")
          b_id = (match.get("entrantB") or {}).get("entrantId")

    results_matches.append({
        **match,
        "entrantA": {
            "entrantId": a_id,
            "name": entrant_lookup.get(a_id, "TBD"),
            "score": (match.get("entrantA") or {}).get("score", "")
        },
        "entrantB": {
            "entrantId": b_id,
            "name": entrant_lookup.get(b_id, "TBD"),
            "score": (match.get("entrantB") or {}).get("score", "")
        }
    })

    for m in results_matches:
        print(
        entrant_lookup.get(m["entrantA"]["entrantId"]),
        m["entrantA"].get("score", "NO SCORE"),
        "-",
        m["entrantB"].get("score", "NO SCORE"),
        entrant_lookup.get(m["entrantB"]["entrantId"])
    )

    print("\nRESULT MATCHES RAW:")
    print("ALLOWED:", allowed_rounds)
    print("HAS CONSOLATION:", config.get("consolationMatch"))

    for m in results_matches:
     print(
        "DEBUG:",
        m.get("roundNum"),
        m.get("id"),
        m.get("entrantA", {}).get("name"),
        "vs",
        m.get("entrantB", {}).get("name")
    )

    for m in results_matches:
        print(
        m.get("roundNum"),
        m.get("entrantA", {}).get("name"),
        "vs",
        m.get("entrantB", {}).get("name")
    )

    print("\nBRACKET KEYS:", bracket_data.keys())
    print("MATCHES COUNT:", len(matches))

    print("RESULT MATCHES:", len(results_matches))

    for m in results_matches:
     print(
        "Round",
        m.get("roundNum"),
        "|",
        m["entrantA"]["name"],
        "vs",
        m["entrantB"]["name"]
    )

    qualified_entrant_ids = set()


    if tier in [3, 4]:
       target_round = total_rounds - 2
    elif tier == 2:
       target_round = total_rounds - 3
    else:
       target_round = total_rounds - 4

    for match in matches:
        if match.get("roundNum") != target_round:
            continue

        a = match.get("entrantA", {}).get("entrantId")
        b = match.get("entrantB", {}).get("entrantId")

        if a:
            qualified_entrant_ids.add(a)
        if b:
            qualified_entrant_ids.add(b)

    print("QUALIFIED:", len(qualified_entrant_ids))

    payout_distribution = []

    for payout in (data.get("payouts") or []):

        title = payout.get("title", "")
        strategy = payout.get("strategy")
        raw = payout.get("payout")

        if "pin" in title.lower():
            continue
        if strategy != "percentage":
            continue
        if raw is None:
            continue

        percentage = int(raw)
        if percentage > 100:
            percentage //= 100

        payout_distribution.append({
            "place_low": payout.get("placeLow"),
            "place_high": payout.get("placeHigh"),
            "percentage": percentage,
        })

    print("DEBUG PAYOUTS:", payout_distribution)


    players = []
    total_teams = len(entrants)
    for entrant in entrants:

        if qualified_entrant_ids and entrant["id"] not in qualified_entrant_ids:
            continue

        team = entrant.get("team", {})
        members = team.get("members", [])

        players.append({
            "team": entrant.get("name", ""),
            "members": [m.get("displayName", "") for m in members]
        })

    date = data.get("startAt", "")[:10]

    socials = data.get("meta", {}).get("eventSocials", {})

    discord = socials.get("discord", "")
    twitter = socials.get("twitter", "")
    youtube = socials.get("youtube", "")
    twitch = socials.get("twitch", "")
    instagram = socials.get("instagram", "")
    facebook = socials.get("facebook", "")

    if "discord.gg/" in discord:
       discord = discord.split("/")[-1]
    elif "discord.com/invite/" in discord:
        discord = discord.split("/")[-1]

    if twitter:
       twitter = twitter.rstrip("/").split("/")[-1]
       twitter = twitter.replace("@", "")

    if youtube:
       youtube = youtube.rstrip("/").split("/")[-1]
       youtube = youtube.replace("@", "")

    if twitch:
     twitch = twitch.rstrip("/").split("/")[-1]

    if instagram:
       instagram = instagram.rstrip("/").split("/")[-1]

    if facebook:
       facebook = facebook.rstrip("/").split("/")[-1]

    format_type = "Double-elimination" if config.get("bracketType") == "double" else "Single-elimination"
    
    rounds_bo = get_rounds_bo(matches, config)
    
    qualified_team_number = len(qualified_entrant_ids) if len(qualified_entrant_ids) == 8 else None

    return {
        "name": data.get("title", ""),
        "prizepool": prizepool,
        "tier": tier,
        "region": REGION_MAP.get(data.get("gameRegionId"), "|country="),
        "url": url,
        "id": tournament_id,
        "date": date,
        "discord": discord,
        "twitter": twitter,
        "youtube": youtube,
        "twitch": twitch,
        "instagram": instagram,
        "organizer": organizer,
        "facebook": facebook,
        "players": players,
        "total_rounds": total_rounds,
        "team_number": len(entrants),
        "qualified_team_number": qualified_team_number,
        "has_qualified_teams": len(qualified_entrant_ids) == 8,
        "has_third_place_match": config.get("consolationMatch", False),
        "payout_distribution": payout_distribution,
        "format_type": format_type,
        "rounds_bo": rounds_bo,
        "third_place_match": third_place_match,
        "total_teams": total_teams,
        "matches": results_matches,
        "entrant_lookup": entrant_lookup,

    }
