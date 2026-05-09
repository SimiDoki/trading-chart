from boto3.dynamodb.conditions import Key
import asyncio, json, boto3, websockets, time, redis, requests

# 1. Listába tesszük a coinokat
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'LINKUSDT', 'SUIUSDT']
TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
REGION = 'eu-central-1'

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
cw = boto3.client('cloudwatch', region_name=REGION)
table = boto3.resource('dynamodb', region_name=REGION).Table('MarketHistory')

last_cw = {}

async def stream_binance():
    # 2. Összerakjuk az összes kombinációt (szimbólum + timeframe)
    streams = []
    for s in SYMBOLS:
        for tf in TIMEFRAMES:
            streams.append(f"{s.lower()}@kline_{tf}")
            
    url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"
    
    print(f"START: {', '.join(SYMBOLS)} | {len(TIMEFRAMES)} TIMEFRAMES")

    async with websockets.connect(url) as ws:
        while True:
            try:
                res = json.loads(await ws.recv())
                data = res['data']
                k = data['k']
                
                # 3. A Binance üzenetéből szedjük ki, melyik coinról van szó
                s = k['s']
                i, p = k['i'], k['c']
                
                # Mentés a helyi Redisbe a megfelelő kulccsal
                r.set(f"{s}_{i}", json.dumps(data))
                
                now = time.time()
                # CloudWatch beküldés coinfüggően (30 mp-enként coinként)
                if i == '1m' and (s not in last_cw or now - last_cw[s] > 30):
                    cw.put_metric_data(
                        Namespace='TradingSystem/LivePrices',
                        MetricData=[{
                            'MetricName': 'CurrentPrice', 
                            'Dimensions': [{'Name': 'Symbol', 'Value': s}], 
                            'Value': float(p)
                        }]
                    )
                    last_cw[s] = now

                # DynamoDB mentés a lezárt gyertyáknál
                if k.get('x'):
                    table.put_item(Item={
                        'PK': f"TICKER#{s}#{i}",
                        'SK': int(k['t']),
                        'o': k['o'], 'h': k['h'], 'l': k['l'], 'c': p, 'v': k['v']
                    })
                    print(f"Saved: {s} {i}")

            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(2)
                break

def backfill_data(symbol, timeframe):
    # 1. Megnézzük az utolsó mentett adatot a DynamoDB-ben
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"TICKER#{symbol}#{timeframe}"),
        ScanIndexForward=False,
        Limit=1
    )
    
    if not response['Items']:
        return # Ha még nincs adat, nincs mit visszatölteni
    
    last_ts = response['Items'][0]['SK']
    now_ts = int(time.time() * 1000)

    # 2. Lekérjük a hiányzó gyertyákat a Binance REST API-ról
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&startTime={last_ts}&limit=1000"
    res = requests.get(url).json()

    # 3. Mentés DynamoDB-be
    for k in res:
        table.put_item(Item={
            'PK': f"TICKER#{symbol}#{timeframe}",
            'SK': int(k[0]),
            'o': k[1], 'h': k[2], 'l': k[3], 'c': k[4], 'v': k[5]
        })
    print(f"Backfill kész: {symbol} {timeframe} ({len(res)} gyertya)")

if __name__ == "__main__":
    # Induláskor minden párra lefuttatjuk a visszatöltést
    for s in SYMBOLS:
        for tf in TIMEFRAMES:
            try:
                backfill_data(s, tf)
            except Exception as e:
                print(f"Backfill hiba ({s}): {e}")

    # Utána jöhet a folyamatos élő stream
    while True:
        try: asyncio.run(stream_binance())
        except: time.sleep(2)