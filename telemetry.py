from pi_analytics import PIAnalytics, Signal
from product_insights import LogManager
from datetime import datetime
import os


def sendSignal(signaltype):
    if os.environ.get("ING_KEY") == None:
        print("please provide ingestion key. skipping signal")
        return
    LogManager.initialize(
        os.environ["ING_KEY"])
    pia = PIAnalytics(
        os.environ["ING_KEY"])
    signal = Signal(
        "immihelp") if signaltype == "immihelp" else Signal("importjob")
    pia.track_signal(signal)
    LogManager.flush_and_tear_down()


if __name__ == "__main__":
    sendSignal("importjob")

    pass
