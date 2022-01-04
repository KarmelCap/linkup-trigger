import datetime
import json
import os

import dateutil.utils
import pytest
from unittest.mock import Mock
import boto3
from linkup import app

os.environ['DESTINATION_QUEUE'] = 'testerqueuer'


@pytest.fixture()
def cloudwatch_event_without_processing_date():
    return {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-2",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        ],
        "detail": {
        }
    }


@pytest.fixture()
def cloudwatch_event_with_processing_date():
    return {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-2",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        ],
        "detail": {
            "start-processing-date": "2021-1-1"
        }
    }


def test_date_range_same_date():
    results = app.build_date_range(dateutil.utils.today(), dateutil.utils.today())
    assert len(results) == 1


def test_date_range_2_days():
    results = app.build_date_range(datetime.datetime.strptime("21-06-2014", "%d-%m-%Y"),
                                   datetime.datetime.strptime("22-06-2014", "%d-%m-%Y"))
    assert len(results) == 2


def test_lambda_handler(cloudwatch_event_without_processing_date):
    queue = Mock()
    queue.send_message("?").get("success")
    app.process(cloudwatch_event_without_processing_date, queue)
    queue.send_message().assert_called_twice()


def test_lambda_handler_with_dates_listing(cloudwatch_event_with_processing_date):
    queue = Mock()
    queue.send_message("?").get("success")
    app.process(cloudwatch_event_with_processing_date, queue)
    queue.send_message().assert_called_twice()
