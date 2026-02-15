import datetime
import time

import pybook.t82 as t


def test_t82_stock_agg_heap():
    aggregator = t.StockAgg(3)
    aggregator.push(datetime.datetime.now(), 5)

    time.sleep(1)
    aggregator.push(datetime.datetime.now(), 8)

    time.sleep(1)
    aggregator.push(datetime.datetime.now(), 2)

    assert aggregator.avg() == 5
    assert aggregator.low() == 2
    assert aggregator.high() == 8

    time.sleep(1)
    assert aggregator.avg() == 5
    assert aggregator.low() == 2
    assert aggregator.high() == 8

    time.sleep(1)
    assert aggregator.avg() == 2
    assert aggregator.low() == 2
    assert aggregator.high() == 2

    time.sleep(1)
    assert aggregator.avg() is None
    assert aggregator.low() is None
    assert aggregator.high() is None


def test_t82_stock_agg_queue():
    aggregator = t.StockAgg(3)
    aggregator.push(datetime.datetime.now(), 5)

    time.sleep(1)
    aggregator.push(datetime.datetime.now(), 8)

    time.sleep(1)
    aggregator.push(datetime.datetime.now(), 2)

    assert aggregator.avg() == 5
    assert aggregator.low_O1() == 2
    assert aggregator.high_O1() == 8

    time.sleep(1)
    assert aggregator.avg() == 5
    assert aggregator.low_O1() == 2
    assert aggregator.high_O1() == 8

    time.sleep(1)
    assert aggregator.avg() == 2
    assert aggregator.low_O1() == 2
    assert aggregator.high_O1() == 2

    time.sleep(1)
    assert aggregator.avg() is None
    assert aggregator.low_O1() is None
    assert aggregator.high_O1() is None
