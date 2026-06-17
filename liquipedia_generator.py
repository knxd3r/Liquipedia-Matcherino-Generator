import random
import string
from collections import defaultdict


def generate_bracket_id():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))


def sanitize(text: str) -> str:
    """
    MediaWiki safe string:
    Removes everything before '|'
    """
    if text is None:
        return "TBD"
    
    text = str(text)
    
    if '|' in text:
        text = text.split('|', 1)[1].strip()
    
    return text


def build_bracket(
    matches,
    entrant_lookup,
    bo_map,
    has_3rd_place=False,
    third_place_match=None
):

    matches = sorted(matches, key=lambda x: x.get("id", 0))

    groups = defaultdict(list)
    for m in matches:
        groups[m.get("roundNum")].append(m)

    sorted_rounds = sorted(groups.keys())

    qf = groups[sorted_rounds[0]] if len(sorted_rounds) > 0 else []
    sf = groups[sorted_rounds[1]] if len(sorted_rounds) > 1 else []
    gf = groups[sorted_rounds[-1]] if sorted_rounds else []

    bracket_id = generate_bracket_id()

    bracket = f"{{{{Bracket|Bracket/8|id={bracket_id}|matchWidth=200\n"

    bracket += "<!-- Quarterfinals -->\n"

    for i, m in enumerate(qf, 1):
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))

        bracket += (
    f"|R1M{i}={{{{Match\n"
    f"|bestof={bo_map.get(1, 3)}\n"
    f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
    f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
    f"}}}}\n"
)


    bracket += "<!-- Semifinals -->\n"
    for i, m in enumerate(sf, 1):
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))


        bracket += (
    f"|R2M{i}={{{{Match\n"
    f"|bestof={bo_map.get(2, 3)}\n"
    f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
    f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
    f"}}}}\n"
)

    if gf:
        m = gf[0]
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))
        bracket += "<!-- Grand Final -->\n"

        bracket += (
    f"|R3M1={{{{Match\n"
    f"|bestof={bo_map.get(3, 5)}\n"
    f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
    f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
    f"}}}}\n"
)

    third_match = third_place_match

    if has_3rd_place and third_match:

     a_id = (third_match.get("entrantA") or {}).get("entrantId")
     b_id = (third_match.get("entrantB") or {}).get("entrantId")

     a_score = (third_match.get("entrantA") or {}).get("score") or 0
     b_score = (third_match.get("entrantB") or {}).get("score") or 0

     a = sanitize(entrant_lookup.get(a_id, "TBD"))
     b = sanitize(entrant_lookup.get(b_id, "TBD"))

     bracket += (
         f"|RxMTP={{{{Match\n"
         f"|bestof={bo_map.get(3, 5)}\n"
         f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
         f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
         f"}}}}\n"
    )

    bracket += "}}"
    return bracket

def generate_page(data):

    slots = []
    third = fourth = None
    combined_34 = None

    for p in data["payout_distribution"]:
        low = p["place_low"]
        high = p["place_high"]
        perc = p["percentage"]

        if perc is None:
            continue

        if low == 1:
            slots.append(f"{{{{Slot|place=1|percentage1={perc}}}}}")

        elif low == 2:
            slots.append(f"{{{{Slot|place=2|percentage1={perc}}}}}")

        elif low == 3 and high == 3:
            third = perc

        elif low == 4 and high == 4:
            fourth = perc

        elif low == 3 and high == 4:
            combined_34 = perc

    if data["has_third_place_match"]:
        if third is not None:
            slots.append(f"{{{{Slot|place=3|percentage1={third}}}}}")
        if fourth is not None:
            slots.append(f"{{{{Slot|place=4|percentage1={fourth}}}}}")
    else:
        if combined_34 is not None:
            slots.append(f"{{{{Slot|place=3-4|percentage1={combined_34}}}}}")
            
        slots.append("{{Slot|place=5-8|percentage1=}}")

    prize_distribution = (
        "{{TeamPrizePool|prizesummary=true|import=true|cutafter=8|percentage1=1"
       + "".join(f"\n|{slot}" for slot in slots)
       + "\n}}"
)

    participants = "{{TeamParticipants\n"

    for team in data["players"]:
        team_name = sanitize(team["team"])

        participants += (

            f"|{{{{Opponent|{team_name}|import=false|qualification="
            f"{{{{Qualification|method=|url=|text=|placement=}}}}\n"
            f"    |players={{{{Persons\n"
        )

        for player in team["members"]:
            player = sanitize(player)
            participants += f"  |{{{{Person|{player}|flag=}}}}\n"

        participants += " }}\n }}\n"

    participants += "}}"
    bracket = build_bracket(
    data["matches"],
    data["entrant_lookup"],
    {
        1: data["other_matches_bo"],
        2: data["other_matches_bo"],
        3: data["grand_final_bo"],
    },
    data["has_third_place_match"],
    data["third_place_match"]
)
    socials = ""
    if data["discord"]:
       socials += f"|discord={data['discord']}\n"
    if data["twitter"]:
       socials += f"|twitter={data['twitter']}\n"
    if data["youtube"]:
        socials += f"|youtube={data['youtube']}\n"
    if data["twitch"]:
       socials += f"|twitch={data['twitch']}\n"
    if data["instagram"]:
       socials += f"|instagram={data['instagram']}\n"
    if data["facebook"]:
       socials += f"|facebook={data['facebook']}\n"

    return f"""{{{{DISPLAYTITLE:{data['name']}}}}}
{{{{Infobox league
<!-- Header -->
|image=Matcherino allmode.png
|icon=Matcherino allmode.png
|name={data['name']}
|tickername={data['name']}
|shortname={data['name']}
<!-- League Information -->
{f"|organizer={data['organizer']}" if data["organizer"] else ""}
{data['region']}
|format={data['format_type']}
|prizepoolusd={data['prizepool']}
|date={data['date']}
|series=
|liquipediatier={data['tier']}
|team_number={data.get('team_number', len(data.get('players', [])))}
|type=Online
<!-- Links -->
|web={data['url']}
|bracket={data['url']}/bracket
|rules={data['url']}/rules
{socials}
<!-- Chronology -->
|previous=
|next=
}}}}

==About==
===Format===
* {data['format_type']} bracket
* Grand Final Match are {{{{Abbr/Bo{data['grand_final_bo']}xBo3}}}}
* All other matches are {{{{Abbr/Bo{data['other_matches_bo']}xBo3}}}}

==Prize Pool==
{prize_distribution}

==Participants==
{participants}

==Results (Top 8)==
{bracket}

==Additional Information==
===Country Representation===
{{{{Country representation}}}}

==References==
{{{{Reflist}}}}
"""
