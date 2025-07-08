
from kafka import KafkaConsumer
import json
import logging
from create_chromadb_embeddings import embed_message


def main():
    consumer = KafkaConsumer(
        'appointments.scheduler.appointment_summary',
        'appointments.scheduler.visit_summary',
        'appointments.scheduler.study_summary',
        'appointments.scheduler.subject_summary',
        'appointments.scheduler.site_summary',  # Debezium CDC topic for your table
        bootstrap_servers=['localhost:29092'],         # Or 9092, depending on your Kafka setup
        value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
        group_id='faiss-processor-group',
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    logging.basicConfig(
        level=logging.INFO,
        filename='/tmp/cdc_listener.log',  # Log file path
        filemode='a',                 # Append mode
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    for message in consumer:
        payload = message.value
        # Debezium CDC event structure: { 'payload': { 'after': {...}, ... } }
        after = payload.get('after')
        if after:
            #print(after)
            #logging.info(f"Processed row: {after}")
            #logging.info(f"Vector embedding: {embedding}")
            embed_message(after)
            #logging.info(f"Processed row:  {after}")
            # Insert your FAISS logic here

if __name__ == "__main__":
    main()
