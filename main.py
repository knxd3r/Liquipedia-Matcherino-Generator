from matcherino_api import get_tournament_data
from liquipedia_generator import generate_page

def main():
    url = input("Вставьте ссылку Matcherino: ").strip()

    print("Получаю данные турнира...")

    data = get_tournament_data(url)

    print("PAYOUT DEBUG:")
    for payout in data.get("payout_distribution", []):
      print(payout)

    print("Генерирую Liquipedia код...")

    page = generate_page(data)

    with open("liquipedia.txt", "w", encoding="utf-8") as f:
        f.write(page)

    print("Сохранено в liquipedia.txt")


if __name__ == "__main__":
    main()