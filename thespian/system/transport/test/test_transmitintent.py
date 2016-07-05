from thespian.system.transport import (TransmitIntent, SendStatus,
                                       MAX_TRANSMIT_RETRIES)
from thespian.system.utilis import timePeriodSeconds
from datetime import datetime, timedelta
from time import sleep


class TestUnitSendStatus(object):

    def testSendStatusSuccess(self):
        assert SendStatus.Sent == SendStatus.Sent
        assert SendStatus.Sent

    def testSendStatusFailures(self):
        assert SendStatus.Failed == SendStatus.Failed
        assert not SendStatus.Failed
        assert SendStatus.NotSent == SendStatus.NotSent
        assert not SendStatus.NotSent
        assert SendStatus.BadPacket == SendStatus.BadPacket
        assert not SendStatus.BadPacket
        assert SendStatus.DeadTarget == SendStatus.DeadTarget
        assert not SendStatus.DeadTarget

    def testSendStatusComparisons(self):
        assert SendStatus.Sent != SendStatus.Failed
        assert SendStatus.Sent != SendStatus.NotSent
        assert SendStatus.Sent != SendStatus.BadPacket
        assert SendStatus.Sent != SendStatus.DeadTarget

        assert SendStatus.Failed != SendStatus.Sent
        assert SendStatus.Failed != SendStatus.NotSent
        assert SendStatus.Failed != SendStatus.BadPacket
        assert SendStatus.Failed != SendStatus.DeadTarget

        assert SendStatus.NotSent != SendStatus.Failed
        assert SendStatus.NotSent != SendStatus.Sent
        assert SendStatus.NotSent != SendStatus.BadPacket
        assert SendStatus.NotSent != SendStatus.DeadTarget

        assert SendStatus.BadPacket != SendStatus.Failed
        assert SendStatus.BadPacket != SendStatus.NotSent
        assert SendStatus.BadPacket != SendStatus.Sent
        assert SendStatus.BadPacket != SendStatus.DeadTarget

        assert SendStatus.DeadTarget != SendStatus.Failed
        assert SendStatus.DeadTarget != SendStatus.NotSent
        assert SendStatus.DeadTarget != SendStatus.BadPacket
        assert SendStatus.DeadTarget != SendStatus.Sent


class TestUnitTransmitIntent(object):

    def testNormalTransmit(self):
        ti = TransmitIntent('addr', 'msg')
        assert ti.targetAddr == 'addr'
        assert ti.message == 'msg'
        assert ti.result == None

    def testNormalTransmitStr(self):
        ti = TransmitIntent('addr', 'msg')
        # Just ensure no exceptions are thrown
        assert str(ti)

    def testNormalTransmitIdentification(self):
        ti = TransmitIntent('addr', 'msg')
        # Just ensure no exceptions are thrown
        assert ti.identify()

    def testNormalTransmitResetAddress(self):
        ti = TransmitIntent('addr', 'msg')
        assert ti.targetAddr == 'addr'
        assert ti.message == 'msg'
        ti.changeTargetAddr('addr2')
        assert ti.targetAddr == 'addr2'
        assert ti.message == 'msg'

    def testNormalTransmitResetMessage(self):
        ti = TransmitIntent('addr', 'msg')
        assert ti.targetAddr == 'addr'
        assert ti.message == 'msg'
        ti.changeMessage('message2')
        assert ti.targetAddr == 'addr'
        assert ti.message == 'message2'

    def testTransmitIntentSetResult(self):
        ti = TransmitIntent('addr', 'msg')
        assert None == ti.result
        ti.result = SendStatus.Sent
        assert ti.result == SendStatus.Sent
        ti.result = SendStatus.Failed
        assert ti.result == SendStatus.Failed

    def testTransmitIntentSetBadResultType(self):
        ti = TransmitIntent('addr', 'msg')
        assert None == ti.result

    def _success(self, result, intent):
        self.successes.append( (result, intent) )
    def _failed(self, result, intent):
        self.failures.append( (result, intent) )

    def testTransmitIntentCallbackSuccess(self):
        ti = TransmitIntent('addr', 'msg')
        ti.result = SendStatus.Sent
        # Ensure no exception thrown
        ti.completionCallback()
        # And again
        ti.completionCallback()

    def testTransmitIntentCallbackFailureNotSent(self):
        ti = TransmitIntent('addr', 'msg')
        ti.result = SendStatus.NotSent
        # Ensure no exception thrown
        ti.completionCallback()
        # And again
        ti.completionCallback()

    def testTransmitIntentCallbackFailureFailed(self):
        ti = TransmitIntent('addr', 'msg')
        ti.result = SendStatus.Failed
        # Ensure no exception thrown
        ti.completionCallback()
        # And again
        ti.completionCallback()

    def testTransmitIntentCallbackSuccessWithTarget(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.Sent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti)]
        assert self.failures == []
        # And again
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti)]
        assert self.failures == []

    def testTransmitIntentCallbackFailureNotSentWithTarget(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.NotSent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti)]
        # And again
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti)]

    def testTransmitIntentCallbackFailureFailedWithTarget(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.Failed
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti)]
        # And again
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti)]

    def testTransmitIntentCallbackSuccessWithChainedTargets(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.addCallback(self._success, self._failed)
        ti.result = SendStatus.Sent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti), (SendStatus.Sent, ti)]
        assert self.failures == []
        # And again
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti), (SendStatus.Sent, ti)]
        assert self.failures == []

    def testTransmitIntentCallbackFailureNotSentWithChainedTargets(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.addCallback(self._success, self._failed)
        ti.result = SendStatus.NotSent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti),
                                 (SendStatus.NotSent, ti)]
        # And again
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti),
                                 (SendStatus.NotSent, ti)]

    def testTransmitIntentCallbackFailureFailedWithChainedTargets(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.addCallback(self._success, self._failed)
        ti.result = SendStatus.Failed
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti),
                                 (SendStatus.Failed, ti)]
        # And again
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti),
                                 (SendStatus.Failed, ti)]

    def testTransmitIntentCallbackSuccessWithChangedTargetsAdded(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.Sent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti)]
        assert self.failures == []
        # And again
        ti.addCallback(self._success, self._failed)
        ti.completionCallback()
        assert self.successes == [(SendStatus.Sent, ti), (SendStatus.Sent, ti)]
        assert self.failures == []

    def testTransmitIntentCallbackFailureNotSentWithChangedTargetsAdded(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.NotSent
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti)]
        # And again
        ti.addCallback(self._success, self._failed)
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.NotSent, ti),
                                 (SendStatus.NotSent, ti)]

    def testTransmitIntentCallbackFailureFailedWithChangedTargetsAdded(self):
        self.successes = []
        self.failures = []
        ti = TransmitIntent('addr', 'msg',
                            onSuccess = self._success,
                            onError = self._failed)
        ti.result = SendStatus.Failed
        # Ensure no exception thrown
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti)]
        # And again
        ti.addCallback(self._success, self._failed)
        ti.completionCallback()
        assert self.successes == []
        assert self.failures == [(SendStatus.Failed, ti),
                                 (SendStatus.Failed, ti)]

    def testTransmitIntentRetry(self):
        ti = TransmitIntent('addr', 'msg')
        for x in range(MAX_TRANSMIT_RETRIES+1):
            assert ti.retry()
        assert not ti.retry()

    def testTransmitIntentRetryTiming(self):
        maxPeriod = timedelta(milliseconds=90)
        period = timedelta(milliseconds=30)
        ti = TransmitIntent('addr', 'msg',
                            maxPeriod=maxPeriod,
                            retryPeriod=period)
        assert not ti.timeToRetry()
        sleep(timePeriodSeconds(period))
        assert not ti.timeToRetry()

        assert ti.retry()
        assert not ti.timeToRetry()
        sleep(timePeriodSeconds(period))
        assert ti.timeToRetry()

        assert ti.retry()
        assert not ti.timeToRetry()
        sleep(timePeriodSeconds(period))
        assert not ti.timeToRetry()  # Each retry increases
        sleep(timePeriodSeconds(period))
        assert ti.timeToRetry()

        assert not ti.retry()  # Exceeds maximum time

    def testTransmitIntentRetryTimingExceedsLimit(self):
        maxPeriod = timedelta(seconds=90)
        period = timedelta(microseconds=1)
        ti = TransmitIntent('addr', 'msg',
                            maxPeriod=maxPeriod,
                            retryPeriod=period)
        assert not ti.timeToRetry()

        for N in range(MAX_TRANSMIT_RETRIES+1):
            # Indicate "failure" and the need to retry
            assert ti.retry()
            # Wait for the indication that it is time to retry
            time_to_retry = False
            for x in range(90):
                # Only call timeToRetry once, because it auto-resets
                time_to_retry = ti.timeToRetry()
                if time_to_retry: break
                sleep(timePeriodSeconds(period) * 1.5)
            assert time_to_retry

        assert not ti.retry()

    def testTransmitIntentDelay(self):
        maxPeriod = timedelta(milliseconds=90)
        period = timedelta(milliseconds=30)
        ti = TransmitIntent('addr', 'msg',
                            maxPeriod=maxPeriod,
                            retryPeriod=period)
        delay = ti.delay()
        assert delay > timedelta(milliseconds=88)
        assert delay < timedelta(milliseconds=91)

    def testTransmitIntentRetryDelay(self):
        maxPeriod = timedelta(milliseconds=90)
        period = timedelta(milliseconds=30)
        ti = TransmitIntent('addr', 'msg',
                            maxPeriod=maxPeriod,
                            retryPeriod=period)
        ti.retry()
        delay = ti.delay()
        assert delay > timedelta(milliseconds=28)
        assert delay < timedelta(milliseconds=31)

    def testTransmitIntentRetryRetryDelay(self):
        maxPeriod = timedelta(milliseconds=90)
        period = timedelta(milliseconds=30)
        ti = TransmitIntent('addr', 'msg',
                            maxPeriod=maxPeriod,
                            retryPeriod=period)
        ti.retry()
        ti.retry()
        delay = ti.delay()
        assert delay > timedelta(milliseconds=58)
        assert delay < timedelta(milliseconds=61)
