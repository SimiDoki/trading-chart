import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
settings_table = dynamodb.Table('UserSettings')
alerts_table = dynamodb.Table('TradingAlerts')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    try:
        user_id = event['requestContext']['authorizer']['jwt']['claims']['sub']
        method = event['requestContext']['http']['method']
        path = event['rawPath']
        
        body = {}
        if event.get('body'):
            try: body = json.loads(event['body'])
            except: pass

        # --- WATCHLIST ---
        if "/watchlist" in path:
            if method == 'GET':
                resp = settings_table.get_item(Key={'userId': user_id})
                watchlist = resp.get('Item', {}).get('watchlist', [])
                return {"statusCode": 200, "headers": headers, "body": json.dumps(list(watchlist))}
            
            elif method == 'POST':
                symbol = body.get('symbol', '').upper()
                settings_table.update_item(
                    Key={'userId': user_id},
                    UpdateExpression="ADD watchlist :s",
                    ExpressionAttributeValues={':s': {symbol}}
                )
                return {"statusCode": 200, "headers": headers, "body": json.dumps({"message": f"{symbol} hozzáadva"})}

            elif method == 'DELETE':
                symbol = body.get('symbol', '').upper()
                settings_table.update_item(
                    Key={'userId': user_id},
                    UpdateExpression="DELETE watchlist :s",
                    ExpressionAttributeValues={':s': {symbol}}
                )
                return {"statusCode": 200, "headers": headers, "body": json.dumps({"message": f"{symbol} törölve"})}

        # --- ALERTS ---
        elif "/alerts" in path:
            if method == 'GET':
                resp = alerts_table.query(KeyConditionExpression=Key('userId').eq(user_id))
                return {"statusCode": 200, "headers": headers, "body": json.dumps(resp.get('Items', []), default=decimal_default)}
            
            elif method == 'POST':
                alert_id = str(uuid.uuid4())[:8]
                target_price = Decimal(str(body.get('targetPrice')))
                
                item = {
                    'userId': user_id,
                    'alertId': alert_id,
                    'symbol': body.get('symbol', '').lower(),
                    'targetPrice': target_price,
                    'condition': body.get('condition'),
                    'isActive': True
                }
                alerts_table.put_item(Item=item)
                return {"statusCode": 201, "headers": headers, "body": json.dumps(item, default=decimal_default)}

            elif method == 'DELETE':
                alert_id = body.get('alertId')
                alerts_table.delete_item(Key={'userId': user_id, 'alertId': alert_id})
                return {"statusCode": 200, "headers": headers, "body": json.dumps({"message": "Alert törölve"})}

    except Exception as e:
        print(f"HIBA: {str(e)}")
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 404, "headers": headers, "body": "Útvonal nem található"}