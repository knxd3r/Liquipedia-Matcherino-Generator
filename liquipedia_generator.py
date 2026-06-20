import random
import string
from collections import defaultdict


def generate_bracket_id():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

def sanitize(text: str) -> str:
    """
    MediaWiki safe string:
    """
    if text is None:
        return "TBD"
    return str(text).replace("|", "{{!}}")

def build_format(data):
    format_text = f"* {data['format_type']} bracket\n"

    rounds_bo = data.get("rounds_bo", [])

    if not rounds_bo:
        return format_text

    total_rounds = len(rounds_bo)

    stages = []

    for idx in range(1, total_rounds + 1):
        bo = rounds_bo[-idx]

        if idx == 1:
            round_name = "Grand Final"
        elif idx == 2:
            round_name = "Semifinals"
        elif idx == 3:
            round_name = "Quarterfinals"
        else:
            stage_size = 2 ** idx
            round_name = f"Round of {stage_size}"

        stages.append((round_name, bo))
        
    groups = []

    current_bo = None
    start = None
    end = None

    for i, (name, bo) in enumerate(stages):
        if current_bo is None:
            current_bo = bo
            start = name
            end = name
            continue

        if bo == current_bo:
            end = name
        else:
            groups.append((start, end, current_bo))
            current_bo = bo
            start = name
            end = name

    groups.append((start, end, current_bo))
    
    if len(groups) == 1:
        _, _, bo = groups[0]
        format_text += f"* All matches are {{{{Abbr/Bo{bo}xBo3}}}}\n"
    
    else:
        for start, end, bo in groups:
            if start == end:
                format_text += f"* {start} is {{{{Abbr/Bo{bo}xBo3}}}}\n"
            else:
                format_text += f"* All matches from {start} to {end} are {{{{Abbr/Bo{bo}xBo3}}}}\n"

    return format_text

def build_bracket(
    matches,
    entrant_lookup,
    rounds_bo,
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
    bracket = f"{{{{Bracket|Bracket/8|id={bracket_id}\n"
    bestofed = False

    bracket += "<!-- Quarterfinals -->\n"
    for i, m in enumerate(qf, 1):
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))
        
        bo = rounds_bo[-3]
        
        bracket += f"|R1M{i}={{{{Match\n"
        if not bestofed:
            bracket += f"|bestof={bo}\n"
            bestofed = True
        bracket += (
        f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
        f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
        f"}}}}\n"
        )

    bracket += "<!-- Semifinals -->\n"
    bestofed = False
    for i, m in enumerate(sf, 1):
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))
        
        bo = rounds_bo[-2]

        bracket += f"|R2M{i}={{{{Match\n"
        if not bestofed:
            bracket += f"|bestof={bo}\n"
            bestofed = True
        bracket += (
        f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
        f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
        f"}}}}\n"
        )

    bracket += "<!-- Grand Final -->\n"
    bestofed = False
    if gf:
        m = gf[0]
        a_id = (m.get("entrantA") or {}).get("entrantId")
        b_id = (m.get("entrantB") or {}).get("entrantId")
        a_score = (m.get("entrantA") or {}).get("score") or 0
        b_score = (m.get("entrantB") or {}).get("score") or 0
        a = sanitize(entrant_lookup.get(a_id, "TBD"))
        b = sanitize(entrant_lookup.get(b_id, "TBD"))
        
        bo = rounds_bo[-1]
        
        bracket += f"|R3M1={{{{Match\n"
        if not bestofed:
            bracket += f"|bestof={bo}\n"
            bestofed = True
        bracket += (
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
            
        bo = rounds_bo[-1]

        bracket += (
            f"<!-- Third Place Match -->\n"
            f"|RxMTP={{{{Match\n"
            f"|opponent1={{{{TeamOpponent|{a}|score={a_score}}}}}\n"
            f"|opponent2={{{{TeamOpponent|{b}|score={b_score}}}}}\n"
            f"}}}}\n"
        )

    bracket += "}}"
    return bracket

def generate_page(data):
    slots = []
    
    prizes = {
        1: None,
        2: None,
        3: None,
        4: None,
        "3-4": None,
        "5-8": None,
    }
    
    last_known_place = 0
    third_place_value = None
    fourth_place_value = None
    
    for p in data["payout_distribution"]:
        low = p["place_low"]
        high = p["place_high"]
        perc = p["percentage"]

        if perc is None:
            continue

        if low != -1 and high != -1:
            if low == 1 and high == 1:
                prizes[1] = perc
                last_known_place = 1
            elif low == 2 and high == 2:
                prizes[2] = perc
                last_known_place = 2
            elif low == 3 and high == 3:
                prizes[3] = perc
                third_place_value = perc
                last_known_place = 3
            elif low == 4 and high == 4:
                prizes[4] = perc
                fourth_place_value = perc
                last_known_place = 4
            elif low == 3 and high == 4:
                prizes["3-4"] = perc
                last_known_place = 4
            elif low == 5 and high == 8:
                prizes["5-8"] = perc
                last_known_place = 8
        else:
            last_known_place += 1
            
            if last_known_place == 1:
                prizes[1] = perc
            elif last_known_place == 2:
                prizes[2] = perc
            elif last_known_place == 3:
                if data["has_third_place_match"]:
                    prizes[3] = perc
                    third_place_value = perc
                else:
                    prizes["3-4"] = perc
            elif last_known_place == 4:
                if data["has_third_place_match"]:
                    prizes[4] = perc
                    fourth_place_value = perc
                else:
                    pass
            elif last_known_place >= 5 and last_known_place <= 8:
                if prizes["5-8"] is None:
                    prizes["5-8"] = perc
                else:
                    prizes["5-8"] += perc

    if not data["has_third_place_match"]:
        if third_place_value is not None and fourth_place_value is not None:
            if third_place_value != fourth_place_value:
                raise ValueError(
                    f"API returned inconsistent data: 3rd place ({third_place_value}%) "
                    f"and 4th place ({fourth_place_value}%) values do not match. "
                    f"Expected equal values when no 3rd place match exists."
                )

    total_percentage = 0
    
    if prizes[1] is not None:
        slots.append(f"{{{{Slot|place=1|percentage1={prizes[1]}}}}}")
        total_percentage += prizes[1]
    else:
        slots.append(f"{{{{Slot|place=1|percentage1=}}}}")
    
    if prizes[2] is not None:
        slots.append(f"{{{{Slot|place=2|percentage1={prizes[2]}}}}}")
        total_percentage += prizes[2]
    else:
        slots.append(f"{{{{Slot|place=2|percentage1=}}}}")
    
    if data["has_third_place_match"]:
        if prizes[3] is not None:
            slots.append(f"{{{{Slot|place=3|percentage1={prizes[3]}}}}}")
            total_percentage += prizes[3]
        else:
            slots.append(f"{{{{Slot|place=3|percentage1=}}}}")
        if prizes[4] is not None:
            slots.append(f"{{{{Slot|place=4|percentage1={prizes[4]}}}}}")
            total_percentage += prizes[4]
        else:
            slots.append(f"{{{{Slot|place=4|percentage1=}}}}")
    else:
        if prizes["3-4"] is not None:
            combined_34 = prizes["3-4"]
            
            if total_percentage + combined_34 * 2 <= 100:
                slots.append(f"{{{{Slot|place=3-4|percentage1={combined_34}}}}}")
                total_percentage += combined_34 * 2
            else:
                slots.append(f"{{{{Slot|place=3-4|percentage1={combined_34 / 2:.1f}}}}}")
                total_percentage += combined_34
        else:
            slots.append("{{Slot|place=3-4|percentage1=}}")
    
    if prizes["5-8"] is not None:
        combined_58 = prizes["5-8"]
        
        if total_percentage + combined_58 * 4 <= 100:
            slots.append(f"{{{{Slot|place=5-8|percentage1={combined_58}}}}}")
            total_percentage += combined_58 * 4
        else:
            slots.append(f"{{{{Slot|place=5-8|percentage1={combined_58 / 4:.1f}}}}}")
            total_percentage += combined_58
    else:
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
            participants += f"        |{{{{Person|{player}|flag=}}}}\n"

        participants += "    }}\n}}\n"

    participants += "}}"
    bracket = build_bracket(
        data["matches"],
        data["entrant_lookup"],
        data["rounds_bo"],
        data["has_third_place_match"],
        data["third_place_match"]
    )
    full_format = build_format(data)
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
{full_format}

===Prize Pool===
{prize_distribution}

==Participants (Top 8)==
{participants}

==Results (Top 8)==
{bracket}

==Additional Information==
===Country Representation===
{{{{Country representation}}}}

==References==
{{{{Reflist}}}}
"""
