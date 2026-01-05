"""Kafka producer utility for testing DWS trade ingestion."""

import json
import sys
from datetime import date, timedelta
from confluent_kafka import Producer
from typing import Dict, Any


def create_trade_message(trade_id: str, version: int, days_from_now: int = 30) -> Dict[str, Any]:
    """Create a sample trade message."""
    today = date.today()
    maturity_date = today + timedelta(days=days_from_now)
    
    return {
        "trade_id": trade_id,
        "version": version,
        "counter_party_id": f"CP-{trade_id}",
        "book_id": "B1",
        "maturity_date": maturity_date.isoformat(),
        "created_date": today.isoformat(),
        "expired": False,
        "quantity": 2
    }


def delivery_report(err, msg):
    """Kafka delivery callback."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def send_trades(bootstrap_servers: str = 'localhost:9092', topic: str = 'dws_trade_store', num_trades: int = 10):
    """Send sample trades to Kafka."""
    # Configure producer
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'trade-producer'
    }
    
    producer = Producer(conf)
    
    print(f"Sending {num_trades} trades to Kafka topic '{topic}'...")
    
    try:
        for i in range(1, num_trades + 1):
            # Create trade message
            trade = create_trade_message(f"T{i}", version=1, days_from_now=30 + i)
            
            # Serialize to JSON
            message = json.dumps(trade)
            
            # Send to Kafka
            producer.produce(
                topic,
                key=trade["trade_id"].encode('utf-8'),
                value=message.encode('utf-8'),
                callback=delivery_report
            )
            
            # Trigger delivery reports
            producer.poll(0)
        
        # Wait for all messages to be delivered
        print("\nWaiting for messages to be delivered...")
        producer.flush()
        
        print(f"\nSuccessfully sent {num_trades} trades to Kafka!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
    finally:
        producer.flush()


def send_invalid_trades(bootstrap_servers: str = 'localhost:9092', topic: str = 'trades'):
    """Send invalid trades for testing validation."""
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'trade-producer'
    }
    
    producer = Producer(conf)
    
    print("Sending invalid trades for testing...")
    
    # Trade with past maturity date
    past_trade = create_trade_message("T_PAST", version=1, days_from_now=-10)
    producer.produce(
        topic,
        value=json.dumps(past_trade).encode('utf-8'),
        callback=delivery_report
    )
    
    # Trade with lower version (send v2 first, then v1)
    high_version = create_trade_message("T_VERSION", version=2)
    producer.produce(
        topic,
        value=json.dumps(high_version).encode('utf-8'),
        callback=delivery_report
    )
    
    producer.flush()
    
    low_version = create_trade_message("T_VERSION", version=1)
    producer.produce(
        topic,
        value=json.dumps(low_version).encode('utf-8'),
        callback=delivery_report
    )
    
    producer.flush()
    print("Invalid trades sent!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Trade Producer')
    parser.add_argument('--bootstrap-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--topic', default='trades', help='Kafka topic')
    parser.add_argument('--num-trades', type=int, default=10, help='Number of trades to send')
    parser.add_argument('--invalid', action='store_true', help='Send invalid trades')
    
    args = parser.parse_args()
    
    if args.invalid:
        send_invalid_trades(args.bootstrap_servers, args.topic)
    else:
        send_trades(args.bootstrap_servers, args.topic, args.num_trades)
