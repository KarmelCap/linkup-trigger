import datetime
import json

import os

import boto3
from datetime import date


def lambda_handler(event, context):
    # event may be the cloudwatch trigger of which we need nothing
    print("LinkUp flow...triggered by event: " + str(event))

    sqs = boto3.resource('sqs')
    process(event, sqs.get_queue_by_name(QueueName=os.environ['DESTINATION_QUEUE']))


def process(event, queue):
    start_processing_date = extract_processing_date_or_today(event)
    print("start_processing_date: " + str(start_processing_date))
    dates_to_process = build_date_range(start_processing_date, date.today())
    print("dates_to_process: " + str(dates_to_process))
    for single_date in dates_to_process:
        pump_sqs_messages(queue, single_date)


def build_date_range(start_date, end_date):
    return [date.today()] + [start_date + datetime.timedelta(days=x) for x in range(0, (end_date - start_date).days)]


def extract_processing_date_or_today(event):
    try:
        return datetime.datetime.strptime(str(event['detail']['start-processing-date']), '%Y-%m-%d').date()
    except KeyError:
        return date.today()


def pump_sqs_messages(queue, single_date):
    formatted_date = single_date.strftime('%Y-%m-%d')
    enqueue(queue, "scrape_daily", formatted_date)
    enqueue(queue, "job_records+descriptions_daily", formatted_date)
    enqueue(queue, "ticker_daily", formatted_date)
    enqueue(queue, "company_reference_daily", formatted_date)


def enqueue(queue, unit_of_work, formatted_date):
    response = queue.send_message(QueueUrl=queue.url, MessageBody=json.dumps(
        {
            "date-to-process": formatted_date,
            "unit-of-work": unit_of_work
        }))
    if response.get('Failed'):
        raise RuntimeError('Unable to enqueue! response: ' + str(response))
