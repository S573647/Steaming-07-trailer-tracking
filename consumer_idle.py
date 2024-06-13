import pika
import json
#import logging
from send_email import send_email 
import smtplib
from util_logger import setup_logger
logger, logname = setup_logger(__file__)
# Configure logging
#logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

def process_idle_queue(ch, method, properties, body):
    try:
        # Ensure correct decoding and strip any unnecessary spaces
                
        body_str = body.decode('utf-8').strip()
        
        # Check if the message is empty or malformed
        if not body_str.startswith('{') or not body_str.endswith('}'):
            logger.error(f"Message {body_str} does not appear to be valid JSON format")
            raise ValueError("Message does not appear to be valid JSON format")

        data = json.loads(body_str)
        
        # Validate keys in the JSON object
        if 'trailer_id' not in data or 'location' not in data or 'arrival_timestamp' not in data:
            logger.error(f"Required key missing in JSON data {body_str}")
            raise KeyError("Required key missing in JSON data")

        subject = f"Trailer {data['trailer_id']} is idle  at {data['location']} arrived on {data['arrival_timestamp']}"
        body = f"Trailer {data['trailer_id']} is idle at {data['location']} arrived on {data['arrival_timestamp']}."
        send_email(subject, body, "kamalini.pradhan@gmail.com")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Email sent for trailer {data['trailer_id']}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except KeyError as e:
        logger.error(f"KeyError: {e}. Invalid message format.")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except ValueError as e:
        logger.error(f"ValueError: {e}. Message format issue.")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred while sending email: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_listening(queue_name, callback_func):
    """Sets up RabbitMQ consumer connections to listen to a specific queue."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(queue=queue_name, on_message_callback=callback_func, auto_ack=False)
        logger.info(f"Listening for messages on {queue_name}. Press CTRL+C to exit.")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Consumer interrupted. Closing connection...")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"AMQP connection error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    queue_name = "idle_queue"
    start_listening(queue_name, process_idle_queue)
    
