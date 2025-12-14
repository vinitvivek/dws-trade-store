"""Tests for Kafka DWS Consumer/Traders."""

import pytest
import json
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.kafka_consumer import KafkaTradeConsumer
from app.models.schemas import TradeCreate


class TestKafkaTradeConsumer:
    """Test cases for Kafka DWS Trade Consumer/Traders."""
    
    def test_parse_trade_message_valid(self, trade_service):
        """Test parsing valid trade message."""
        consumer = KafkaTradeConsumer(trade_service)
        
        today = date.today()
        future_date = today + timedelta(days=30)
        
        message = json.dumps({
            "trade_id": "T1",
            "version": 1,
            "counter_party_id": "CP-1",
            "book_id": "B1",
            "maturity_date": future_date.isoformat(),
            "created_date": today.isoformat(),
            "expired": False
        })
        
        result = consumer.parse_trade_message(message)
        
        assert isinstance(result, TradeCreate)
        assert result.trade_id == "T1"
        assert result.version == 1
        assert result.maturity_date == future_date
    
    def test_parse_trade_message_invalid_json(self, trade_service):
        """Test parsing invalid JSON message."""
        consumer = KafkaTradeConsumer(trade_service)
        
        invalid_message = "not a valid json"
        
        with pytest.raises(Exception):
            consumer.parse_trade_message(invalid_message)
    
    def test_parse_trade_message_missing_fields(self, trade_service):
        """Test parsing message with missing required fields."""
        consumer = KafkaTradeConsumer(trade_service)
        
        incomplete_message = json.dumps({
            "trade_id": "T1",
            "version": 1
            # Missing other required fields
        })
        
        with pytest.raises(Exception):
            consumer.parse_trade_message(incomplete_message)
    
    @patch('app.services.kafka_consumer.Consumer')
    def test_process_message_success(self, mock_consumer_class, trade_service, sample_trade_dict):
        """Test successful message processing."""
        consumer = KafkaTradeConsumer(trade_service)
        
        # Create mock Kafka message
        mock_msg = Mock()
        mock_msg.value.return_value = json.dumps(sample_trade_dict).encode('utf-8')
        
        result = consumer.process_message(mock_msg)
        
        assert result is True
    
    @patch('app.services.kafka_consumer.Consumer')
    def test_process_message_validation_error(self, mock_consumer_class, trade_service):
        """Test message processing with validation error."""
        consumer = KafkaTradeConsumer(trade_service)
        
        # Create trade with past maturity date
        today = date.today()
        past_date = today - timedelta(days=10)
        
        invalid_trade = {
            "trade_id": "T1",
            "version": 1,
            "counter_party_id": "CP-1",
            "book_id": "B1",
            "maturity_date": past_date.isoformat(),
            "created_date": today.isoformat(),
            "expired": False
        }
        
        mock_msg = Mock()
        mock_msg.value.return_value = json.dumps(invalid_trade).encode('utf-8')
        
        result = consumer.process_message(mock_msg)
        
        assert result is False
    
    @patch('app.services.kafka_consumer.Consumer')
    def test_process_message_parse_error(self, mock_consumer_class, trade_service):
        """Test message processing with parse error."""
        consumer = KafkaTradeConsumer(trade_service)
        
        mock_msg = Mock()
        mock_msg.value.return_value = b"invalid json"
        
        result = consumer.process_message(mock_msg)
        
        assert result is False
    
    @patch('app.services.kafka_consumer.Consumer')
    def test_consumer_initialization(self, mock_consumer_class, trade_service):
        """Test consumer initialization."""
        consumer = KafkaTradeConsumer(trade_service)
        
        assert consumer.trade_service == trade_service
        assert consumer.running is False
        assert mock_consumer_class.called
    
    @patch('app.services.kafka_consumer.Consumer')
    def test_stop_consumer(self, mock_consumer_class, trade_service):
        """Test stopping the consumer."""
        mock_consumer_instance = Mock()
        mock_consumer_class.return_value = mock_consumer_instance
        
        consumer = KafkaTradeConsumer(trade_service)
        consumer.running = True
        
        consumer.stop()
        
        assert consumer.running is False
        mock_consumer_instance.close.assert_called_once()


class TestKafkaConsumerIntegration:
    """Integration tests for Kafka consumer."""
    
    @pytest.mark.integration
    @pytest.mark.kafka
    def test_consume_batch_integration(self, trade_service, sample_trade_dict):
        """Integration test for batch consumption (requires Kafka)."""
        # This test would require a running Kafka instance
        # Skip if Kafka is not available
        pytest.skip("Requires running Kafka instance")
    
    @pytest.mark.integration
    @pytest.mark.kafka
    def test_end_to_end_message_flow(self, trade_service):
        """End-to-end test from Kafka to database (requires Kafka)."""
        # This test would require a running Kafka instance and database
        pytest.skip("Requires running Kafka and database")