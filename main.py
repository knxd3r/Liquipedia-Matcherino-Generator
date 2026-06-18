import logging
from matcherino_api import get_tournament_data
from liquipedia_generator import generate_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(debug=False):
    url = input("Input Matcherino link: ").strip()

    if not url.startswith("http"):
        logger.error("Wrong URL")
        return 1

    logger.info("Collecting tournament data...")

    try:
        data = get_tournament_data(url)
    except Exception as e:
        logger.error(f"Error with data recieving: {e}")
        return 1

    if debug:
        logger.info("PAYOUT DEBUG:")
        for payout in data.get("payout_distribution", []):
            print(payout)

    logger.info("Generating Liquipedia code...")

    try:
        page = generate_page(data)
    except Exception as e:
        logger.error(f"Error with page generation: {e}")
        return 1

    with open("liquipedia.txt", "w", encoding="utf-8") as f:
        f.write(page)

    logger.info("Saved to liquipedia.txt")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(debug=True))
