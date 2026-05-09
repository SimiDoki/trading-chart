import boto3
import json

cw = boto3.client('cloudwatch', region_name='eu-central-1')
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('TradingAlerts')

def lambda_handler(event, context):
    try:
        # 1. Kinyerjük az SNS üzenetet
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = sns_message['AlarmName'] 
        new_state = sns_message['NewStateValue'] 

        if new_state == 'ALARM':
            print(f"DEBUG: Riasztás észlelve: {alarm_name}")

            # 2. ADATBÁZIS: isActive -> False
            parts = alarm_name.split('#')
            if len(parts) >= 4:
                user_id = parts[1]
                alert_id = parts[3]

                table.update_item(
                    Key={'userId': user_id, 'alertId': alert_id},
                    UpdateExpression="SET isActive = :val",
                    ExpressionAttributeValues={':val': False}
                )
                print(f"SIKER: Adatbázis frissítve (isActive: False)")

                # 3. CLOUDWATCH: Alarm törlése
                cw.delete_alarms(AlarmNames=[alarm_name])
                print(f"SIKER: CloudWatch Alarm törölve: {alarm_name}")
            
            else:
                print(f"HIBA: Rossz alarm név formátum: {alarm_name}")
            
    except Exception as e:
        print(f"HIBA az AlertHandler-ben: {str(e)}")

    return {"status": "processed"}