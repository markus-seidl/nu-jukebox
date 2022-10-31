import math
from pydub import AudioSegment
import pyaudio
import alsaaudio
import threading
import time
import typing


class _AudioManagerData:
    def __init__(self):
        self.audio_playing: typing.Optional[AudioSegment] = None
        self.next_audio: typing.Optional[AudioSegment] = None
        self.stop_playing: bool = False

        self._is_playing_lock = threading.Lock()
        self._is_playing: bool = False
        self.exit: bool = False

    def is_playing(self) -> bool:
        self._is_playing_lock.acquire()
        try:
            return self._is_playing
        finally:
            self._is_playing_lock.release()

    def set_playing(self, val):
        self._is_playing_lock.acquire()
        try:
            self._is_playing = val
        finally:
            self._is_playing_lock.release()


class AudioManager:
    def __init__(self, alsa_idx, alsa_mixer_name, pyaudio_idx):
        self.alsa_idx = alsa_idx
        self.alsa_mixer_name = alsa_mixer_name
        self.pyaudio_idx = pyaudio_idx
        self._tdata = _AudioManagerData()

        self.pyaudio = pyaudio.PyAudio()

        self.mixer = alsaaudio.Mixer(self.alsa_mixer_name, cardindex=self.alsa_idx)
        self._play_thread = threading.Thread(target=self._loop, args=())
        self._play_thread.start()

    @staticmethod
    def from_card_name(alsa_card_name: str, alsa_mixer_name: str):
        alsa_cards = alsaaudio.cards()
        alsa_card_idx = -1
        print(f"ALSA cards: {alsa_cards}")
        for i in range(len(alsa_cards)):
            alsa_card = alsa_cards[i]
            if alsa_card == alsa_card_name:
                alsa_card_idx = i
                break

        p = pyaudio.PyAudio()
        pyaudio_idx = -1
        for i in range(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            print(f"py audio device: {device}")
            if str(device['name']).startswith(alsa_card_name):
                pyaudio_idx = i
                break

        if pyaudio_idx < 0 or alsa_card_idx < 0:
            raise OSError(f"Unable to find pyaudio or alsa card {alsa_card_idx}:{pyaudio_idx}")

        print(f"Found ids: {alsa_card_idx}:{pyaudio_idx}")
        return AudioManager(alsa_card_idx, alsa_mixer_name, pyaudio_idx)

    def set_volume(self, volume):
        volume = int(min(max(0, 50 + volume / 2), 100))
        self.mixer.setvolume(volume)

    def get_volume(self) -> int:
        ret = self.mixer.getvolume()[0]
        print(f"Raw volume: {ret}")
        return max(min((ret - 50) * 2, 100), 0)

    def load_audio(self, file_name: str) -> AudioSegment:
        return AudioSegment.from_file(file_name)

    def play(self, segment: AudioSegment):
        self._tdata.stop_playing = False
        self._tdata.next_audio = segment

    def stop(self):
        self._tdata.next_audio = None
        self._tdata.stop_playing = True

    def block_while_playing(self):
        if not self._tdata.is_playing():
            # not yet playing, wait for it
            counter = 20
            while not self._tdata.is_playing():
                time.sleep(0.1)
                if counter <= 0:
                    break
                counter -= 1

        while self._tdata.is_playing():
            time.sleep(0.1)

        print(f"Finished blocking and playing stopped")

    def shutdown(self):
        self.stop()
        self._tdata.exit = True
        self._play_thread.join()

    def _loop(self):
        """Background loop to play audio"""

        while True:
            if self._tdata.next_audio is not None:
                self._tdata.audio_playing = self._tdata.next_audio
                self._tdata.next_audio = None

                p = self.pyaudio
                seg = self._tdata.audio_playing
                stream = p.open(format=p.get_format_from_width(seg.sample_width),
                                channels=seg.channels,
                                rate=seg.frame_rate,
                                output=True, output_device_index=self.pyaudio_idx)

                # Just in case there were any exceptions/interrupts, we release the resource
                # So as not to raise OSError: Device Unavailable should play() be used again
                try:
                    self._tdata.set_playing(True)
                    print("Started playing")
                    # break audio into half-second chunks (to allows keyboard interrupts)
                    for chunk in _make_chunks(self._tdata.audio_playing, 500):
                        stream.write(chunk._data)

                        if self._tdata.next_audio is not None or self._tdata.stop_playing:
                            print(f"Stopping: {self._tdata.next_audio is not None}:{self._tdata.stop_playing}")
                            break

                        if self._tdata.exit:
                            print("Exiting")
                            return

                        time.sleep(0.01)
                    print("Finished playing")
                except:
                    print("Some error...??")
                    p.terminate()
                    self.pyaudio = pyaudio.PyAudio()
                finally:
                    stream.stop_stream()
                    stream.close()
                    print("Finished closing")
                    self._tdata.audio_playing = None
                    self._tdata.stop_playing = False
                    self._tdata.set_playing(False)

            if self._tdata.exit:
                return

            time.sleep(0.1)


def _make_chunks(audio_segment, chunk_length):
    """
    Breaks an AudioSegment into chunks that are <chunk_length> milliseconds
    long.
    if chunk_length is 50 then you'll get a list of 50 millisecond long audio
    segments back (except the last one, which can be shorter)
    """
    number_of_chunks = math.ceil(len(audio_segment) / float(chunk_length))
    return [audio_segment[i * chunk_length:(i + 1) * chunk_length]
            for i in range(int(number_of_chunks))]


if __name__ == "__main__":
    am = AudioManager(2, "Digital", 1)

    cow = am.load_audio("/home/pi/cow.mp3")
    print(am.get_volume())

    am.play(cow)

    am._play_thread.join()
