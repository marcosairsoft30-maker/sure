import requests

API_KEY = '91e311859bbb1083d22bed4c5acd8622'
BASE_URL_SPORTS = 'https://api.the-odds-api.com/v4/sports'
BASE_URL_ODDS = 'https://api.the-odds-api.com/v4/sports'

def get_all_sports():
    url = BASE_URL_SPORTS
    params = {'apiKey': API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_odds_for_sport(sport_key, regions='us', markets=None):
    url = f'{BASE_URL_ODDS}/{sport_key}/odds'
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'markets': markets if markets else '',  # vazio para pegar todos mercados
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def find_sure_bets_all_markets(odds_data):
    sure_bets = []
    for event in odds_data:
        for bookie in event.get('bookmakers', []):
            for market in bookie.get('markets', []):
                outcomes = market.get('outcomes', [])
                if len(outcomes) < 2:
                    continue
                inv_sum = sum(1/outcome['price'] for outcome in outcomes if outcome['price'] > 0)
                if inv_sum < 1:
                    profit_percent = (1 - inv_sum) * 100
                    sure_bets.append({
                        'event': f"{event['home_team']} x {event['away_team']}",
                        'bookmaker': bookie['title'],
                        'market': market['key'],
                        'outcomes': [(o['name'], o['price']) for o in outcomes],
                        'profit_percent': profit_percent
                    })
    return sure_bets

def main_all_sports_all_markets():
    all_sure_bets = []
    sports = get_all_sports()
    print(f"Esportes encontrados: {[sport['key'] for sport in sports]}")
    for sport in sports:
        try:
            print(f"Buscando odds para o esporte: {sport['key']}")
            odds = get_odds_for_sport(sport['key'], markets='')  # vazio = todos mercados
            sure_bets = find_sure_bets_all_markets(odds)
            if sure_bets:
                print(f"Found {len(sure_bets)} sure bets in {sport['key']}")
                all_sure_bets.extend(sure_bets)
            else:
                print(f"Nenhuma sure bet encontrada em {sport['key']}.")
        except Exception as e:
            print(f"Erro ao buscar odds para {sport['key']}: {e}")
    return all_sure_bets

if __name__ == "__main__":
    bets = main_all_sports_all_markets()
    print(f"\nTotal de sure bets encontradas: {len(bets)}")
    for bet in bets:
        print(f"{bet['event']} | {bet['bookmaker']} | Mercado: {bet['market']} | Resultados: {bet['outcomes']} | Lucro: {bet['profit_percent']:.2f}%")
