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
        'appointments.scheduler.site_summary',
        bootstrap_servers=['localhost:29092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
        group_id='faiss-processor-group',
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    logging.basicConfig(
        level=logging.INFO,
        filename='/tmp/cdc_listener.log',
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    logging.info("Kafka CDC Listener started.")

    for message in consumer:
        raw_value = message.value

        # Adjust for Debezium wrapping (value is wrapped as 'payload')
        payload = raw_value.get("payload") or raw_value
        after = payload.get("after") if payload else None

        if after:
            logging.info(f"[CDC] Received message with after: {after}")
            try:
                embed_message(after)
                logging.info(" embed_message() processed successfully")
            except Exception as e:
                logging.error(f"Error in embed_message: {e}\nMessage: {after}")
        else:
            logging.warning(f" Kafka message missing 'after': {raw_value}")


if __name__ == "__main__":
    main()
