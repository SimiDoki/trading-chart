import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserSettings')

def lambda_handler(event, context):
    print("Beérkező esemény:", json.dumps(event))
    
    # Adatok kinyerése
    user_attrs = event.get('request', {}).get('userAttributes', {})
    user_id = user_attrs.get('sub') or event.get('userName')
    email = user_attrs.get('email')
    
    # Időbélyeg
    now = datetime.utcnow().isoformat()
    
    try:
        table.put_item(
            Item={
                'userId': user_id,
                'email': email if email else "nincs@email.com",
                'contactType': 'email',
                'theme': 'dark',
                'createdAt': now,
                'status': 'active'
            }
        )
        print(f"Sikeres mentés: {user_id}")
        
    except Exception as e:
        print(f"HIBA a mentés során: {str(e)}")
    
    return event