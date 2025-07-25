import sys
from datetime import datetime, timedelta
import platform
import aiohttp
import asyncio
import json


# Перевірка введених даних командного рядку

def parse_sys_argv(argv):
    if len(argv) == 1:
        print("You have to add the argument from 1 to 10! Try again")
        sys.exit(1)

    if len(argv) > 2:
        print("You have to add only one argument! Try again")
        sys.exit(1)

    if len(argv) == 2:
        # Перший аргумент (після назви скрипта)
        try:
            number = int(argv[1])
            if 1 <= number <= 10:
                return number
            else:
                print("Number must be between 1 and 10!")
                sys.exit(1)
        except ValueError:
            print("Enter a number from 1 to 10 as an argument! Try again")
            sys.exit(1)

# Формування списку дат для запитів

def create_date_list(number_of_days):
    list_of_dates = []
    today = datetime.today()
    for i in range(number_of_days):
        new_date = today - timedelta(days = i)
        list_of_dates.append(new_date.strftime("%d.%m.%Y"))
    return list_of_dates

# Формування url для запитів

def get_urls(dates):
    urls = []
    base_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
    for date in dates:
        url = base_url + date
        urls.append(url)
    return urls

# Асинхронний запуск сесій

async def main():
    result = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data =  await resp.json()
                        rates = data.get("exchangeRate", [])
                        filtered = [r for r in rates if r.get("currency") in ("EUR", "USD")]
                        currency = {}
                        for rate in filtered:
                            currency[rate['currency']] = {'sale' : rate['saleRate'], 'purchase' : rate['purchaseRate']}
                        result_of_date = {}
                        result_of_date[url.split('=')[-1]] = currency
                        result.append(result_of_date)
                    else:
                        print(f"Error status: {resp.status} for {url}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {url}', str(err))
        return result
    


if __name__ == "__main__":
    
    number_of_days = parse_sys_argv(sys.argv) # дістаємо з командного рядка кількість днів
    list_of_dates = create_date_list(number_of_days) # формуємо дати, по яких робитимемо запити
    urls = get_urls(list_of_dates) # формуємо список url для запитів
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(main())
        print(json.dumps(result, indent=2, ensure_ascii=False))

