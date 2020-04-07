from pi_analytics import PIAnalytics, Signal
from product_insights import LogManager
from datetime import datetime
import os
import sys


def sendSignal(signaltype):
    if signaltype == None:
       signaltype = "importjob"
    if os.environ.get("ING_KEY") == None:
        print("please provide ingestion key. skipping signal")
        return
    LogManager.initialize(
        os.environ["ING_KEY"])
    pia = PIAnalytics(
        os.environ["ING_KEY"])
    signal = Signal(signaltype)
    pia.track_signal(signal)
    LogManager.flush_and_tear_down()


if __name__ == "__main__":
    sendSignal(sys.argv[1] if len(sys.argv)>1 else "importjob")

    pass
