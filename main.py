import asyncio
import aiohttp
import json
from datetime import datetime

URLS = {
    "makes":         "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json",
    "honda_models":  "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/honda?format=json",
    "toyota_models": "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/toyota?format=json",
    "bmw_models":    "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/bmw?format=json",
}

sem = asyncio.Semaphore(3)

async def fetch(name, url, session):
    async with sem:
        try:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"[OK]    {name}: получено {len(data.get('Results', []))} записей")
                    return data
                print(f"[HTTP {resp.status}] {url}")
        except asyncio.TimeoutError:
            print(f"[ТАЙМАУТ] {url}")
        except Exception as e:
            print(f"[ОШИБКА] {e} ({url})")
        return None


async def get_cars():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(name, url, session) for name, url in URLS.items()]
        results = await asyncio.gather(*tasks)
        return {
            "data": dict(zip(URLS.keys(), results)),
            "timestamp": datetime.now().isoformat(),
        }


def save(data, filename="cars.json"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


async def main():
    while True:
        data = await get_cars()
        save(data)
        print(f"\nДанные сохранены в cars.json ({data['timestamp']})\n")
        await asyncio.sleep(600) 


if __name__ == "__main__":
    asyncio.run(main())
