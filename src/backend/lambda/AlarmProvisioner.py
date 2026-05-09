import boto3
import re
import json

cw = boto3.client('cloudwatch', region_name='eu-central-1')
sns = boto3.client('sns', region_name='eu-central-1')
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
user_settings_table = dynamodb.Table('UserSettings')

def lambda_handler(event, context):
    print("DEBUG: Beérkező esemény:", json.dumps(event))
    
    for record in event.get('Records', []):
        # --- 1. LÉTREHOZÁS ÉS MÓDOSÍTÁS ---
        if record['eventName'] in ['INSERT', 'MODIFY']:
            try:
                new_image = record['dynamodb']['NewImage']
                symbol = new_image['symbol']['S']
                alert_id = new_image['alertId']['S']
                user_id = new_image['userId']['S']
                condition = new_image['condition']['S']
                tp_data = new_image['targetPrice']
                target_price = float(tp_data.get('N') or tp_data.get('S'))
                
                user_resp = user_settings_table.get_item(Key={'userId': user_id})
                if 'Item' not in user_resp: continue
                
                email = user_resp['Item'].get('email')
                if not email: continue

                safe_user_id = re.sub(r'[^a-zA-Z0-9_]', '_', user_id)
                topic_resp = sns.create_topic(Name=f"Alerts_{safe_user_id[:50]}")
                topic_arn = topic_resp['TopicArn']
                
                sns.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint=email)
                
                alarm_name = f"PriceAlert#{user_id}#{symbol}#{alert_id}"
                cw.put_metric_alarm(
                    AlarmName=alarm_name,
                    ComparisonOperator='GreaterThanThreshold' if condition == 'above' else 'LessThanThreshold',
                    EvaluationPeriods=1,
                    MetricName='CurrentPrice',
                    Namespace='TradingSystem/LivePrices',
                    Period=60,
                    Statistic='Maximum',
                    Threshold=target_price,
                    ActionsEnabled=True,
                    AlarmActions=[topic_arn],
                    Dimensions=[{'Name': 'Symbol', 'Value': symbol.upper()}],
                    AlarmDescription=f"SimiPulse: {symbol} elérte a {target_price} árat.",
                    TreatMissingData='notBreaching'
                )
                print(f"SIKER: Alarm beállítva/frissítve: {alarm_name}")

            except Exception as e:
                print(f"HIBA (INSERT/MODIFY): {str(e)}")

        # --- 2. TÖRLÉS KEZELÉSE ---
        elif record['eventName'] == 'REMOVE':
            try:
                old_image = record['dynamodb']['OldImage']
                symbol = old_image['symbol']['S']
                alert_id = old_image['alertId']['S']
                
                alarm_name = f"PriceAlert-{symbol}-{alert_id}"
                
                cw.delete_alarms(AlarmNames=[alarm_name])
                
                print(f"SIKER: Alarm törölve a CloudWatch-ból: {alarm_name}")
                
            except Exception as e:
                print(f"HIBA (REMOVE): {str(e)}")

    return {"status": "done"}