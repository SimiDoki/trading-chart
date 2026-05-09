from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import boto3
from boto3.dynamodb.conditions import Key
import redis
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REGION = "eu-central-1"
TABLE_NAME = "MarketHistory"
REDIS_HOST = "localhost"

r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

@app.get("/api/history/{symbol}/{interval}")
def get_history(symbol: str, interval: str):
    try:
        pk_value = f"TICKER#{symbol.upper()}#{interval}"
        
        response = table.query(
            KeyConditionExpression=Key('PK').eq(pk_value),
            ScanIndexForward=False
        )
        items = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk_value),
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
            
        history = []
        for item in items:
            history.append({
                "k": {
                    "t": int(item['SK']), 
                    "o": str(item['o']), 
                    "h": str(item['h']), 
                    "l": str(item['l']), 
                    "c": str(item['c']), 
                    "v": str(item.get('v', "0")),
                    "s": symbol.upper()
                }
            })
            
        return history[::-1]
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/live/{symbol}/{interval}")
def get_live(symbol: str, interval: str, response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    try:
        redis_key = f"{symbol.upper()}_{interval}"
        data = r.get(redis_key)
        
        if data:
            return json.loads(data)
        else:
            return {"error": "Nincs adat a Redis-ben ehhez a párhoz"}
            
    except Exception as e:
        return {"error": f"Redis hiba: {str(e)}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)