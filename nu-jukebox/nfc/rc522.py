import RPi.GPIO as GPIO
import pirc522
import threading


class _RFIDManagerData:
    def __init__(self):
        self.read_callback = None
        self.stop: bool = False


class RC522Manager:
    def __init__(self, read_callback):
        self.device = pirc522.RFID(
            bus=0,
            device=0,
            pin_rst=25,
            pin_irq=24,
            antenna_gain=4,
            pin_mode=GPIO.BCM
        )

        self._tdata = _RFIDManagerData()
        self._tdata.read_callback = read_callback
        self._search_thread = threading.Thread(target=self._loop, args=())
        self._search_thread.start()

    def shutdown(self):
        self._tdata.stop = True
        self._search_thread.join()
        self.device.cleanup()

    def _loop(self):
        last_card_id = None
        while not self._tdata.stop:
            self.wait_for_tag()
            uid = self.device.read_id(as_number=True)
            if uid is not None:
                if last_card_id is None:
                    uid = f"{uid:X}"
                    print(f'New card found: {uid}')
                    last_card_id = uid
                    if self._tdata.read_callback is not None:
                        self._tdata.read_callback(uid, True)
            else:
                # print("Card no longer found")
                last_card_id = None
                if self._tdata.read_callback is not None:
                    self._tdata.read_callback(uid, False)

    def wait_for_tag(self, loop_increment=5) -> bool:
        if self.device.pin_irq is None:
            raise NotImplementedError('Waiting not implemented if IRQ is not used')

        # enable IRQ on detect
        self.device.init()
        self.device.irq.clear()
        self.device.dev_write(0x04, 0x00)
        self.device.dev_write(0x02, 0xA0)
        # wait for it
        waiting = True
        while waiting:
            self.device.init()
            self.device.dev_write(0x04, 0x00)
            self.device.dev_write(0x02, 0xA0)

            self.device.dev_write(0x09, 0x26)
            self.device.dev_write(0x01, 0x0C)
            self.device.dev_write(0x0D, 0x87)
            waiting = not self.device.irq.wait(0.1)
            if loop_increment <= 0:
                return False
            loop_increment -= 1
        self.device.irq.clear()
        self.device.init()
        return True


if __name__ == "__main__":
    r = RC522Manager(None)

    r._search_thread.join()
