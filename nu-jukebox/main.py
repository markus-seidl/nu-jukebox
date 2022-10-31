import random
import time
import audio
import os
from nfc.rc522 import RC522Manager

AUDIO_ROOT = "/root/audio"
ALBUM_DIE_30_TEIL_1 = AUDIO_ROOT + "/Die_30_schoensten_Kinderlieder_Teil_1/"
ALBUM_SONNTAG_VOL_2 = AUDIO_ROOT + "/Die_60_Besten_Kinderlieder_Vol_2/"
ANIMALS_ROOT = AUDIO_ROOT + "/animals/"

CARD_DICTIONARY = {
    "4278CC3C": {"file": ANIMALS_ROOT + "cow.wav"},
    "F3A7C117": {"file": [ANIMALS_ROOT + "cock.wav", ANIMALS_ROOT + "rooster.wav"]},
    "3309B917": {"file": ANIMALS_ROOT + "dog.wav"},
    "TODO4": {"file": ANIMALS_ROOT + "ducks.wav"},
    "A3BF1716": {"file": ANIMALS_ROOT + "frogs.wav"},
    "5376CE17": {"file": ANIMALS_ROOT + "raven.wav"},
    "A3BF7517": {"file": ANIMALS_ROOT + "sheep.wav"},
    "F319C417": {"file": ANIMALS_ROOT + "cockatoo.wav"},
    "C2A9AD3C": {"file": ALBUM_DIE_30_TEIL_1 + "06 Fuchs_ du hast die Gans gestohlen.wav"},
    "B2AEAD3C": {"file": ALBUM_DIE_30_TEIL_1 + "07 Kuckuck_ Kuckuck ruft_s aus dem Wald.wav"},
    "42D25C3D": {"file": ALBUM_DIE_30_TEIL_1 + "10 Backe_ backe Kuchen.wav"},
    "D2A4AD3C": {"file": ALBUM_DIE_30_TEIL_1 + "11 Wer will fleissige Handwerker sehen.wav"},
    "D27D673D": {"file": ALBUM_DIE_30_TEIL_1 + "26 Summ_ summ_ summ_ Bienchen summ herum.wav"},
    "D278673D": {"file": ALBUM_DIE_30_TEIL_1 + "22 Mein Hut_ der hat drei Ecken.wav"},
    "B3D27317": {"file": ALBUM_DIE_30_TEIL_1 + "14 Die Vogelhochzeit.wav"},
    "63FCCB17": {"file": AUDIO_ROOT + "/miffi-titelsong.wav"},
    "D3CB4493": {"file": ALBUM_SONNTAG_VOL_2 + "/08 Barbie Girl.wav"},
    "3381CB17": {"file": ALBUM_SONNTAG_VOL_2 + "/06 Das rote Pferd.wav"},
    "63340F16": {"file": ALBUM_SONNTAG_VOL_2 + "/02 Gangnam Style.wav"},
    "438CDD15": {"file": ALBUM_SONNTAG_VOL_2 + "/48 Die Finger wollen tanzen.wav"},
    "F324C815": {"file": ALBUM_SONNTAG_VOL_2 + "/27 Auf den Schultern von meinem Dad.wav"},
    "635E1316": {"random_song": ALBUM_SONNTAG_VOL_2},
    "42D75C3D": {"volume_up": 5},
    "42DC5C3D": {"volume_down": 5}
}

ALSA_CARD_NAME = "IQaudIODAC"
ALSA_MIXER_NAME = "Digital"
STARTUP_SOUND = [
    ANIMALS_ROOT + "cow.wav", ANIMALS_ROOT + "dog.wav", ANIMALS_ROOT + "rooster.wav", ANIMALS_ROOT + "sheep.wav",
    ANIMALS_ROOT + "frogs.wav", ANIMALS_ROOT + "cockatoo.wav"
]
VOLUME_UP_SOUND = "/home/pi/audio/volume_up.wav"
VOLUME_DOWN_SOUND = "/home/pi/audio/volume_down.wav"


def card_found_callback(audio_manager: audio.AudioManager, uid, card_on_reader):
    if not card_on_reader:
        audio_manager.stop()
    elif uid in CARD_DICTIONARY:
        card = CARD_DICTIONARY[uid]
        if "file" in card and card_on_reader:
            handle_card_file(card, audio_manager, uid)
        elif "volume_up" in card and card_on_reader:
            handle_card_volume_up(card, audio_manager, uid)
        elif "volume_down" in card and card_on_reader:
            handle_card_volume_down(card, audio_manager, uid)
        elif "random_song" in card and card_on_reader:
            handle_card_random_song(card, audio_manager, uid)
    else:
        print(f"Card not found: {uid}")


def handle_card_volume_up(card, audio_manager: audio.AudioManager, uid):
    amount = card['volume_up']
    audio_manager.set_volume(audio_manager.get_volume() + amount)

    s = audio_manager.load_audio(VOLUME_UP_SOUND)
    audio_manager.play(s)
    audio_manager.block_while_playing()


def handle_card_volume_down(card, audio_manager: audio.AudioManager, uid):
    amount = card['volume_down']
    audio_manager.set_volume(audio_manager.get_volume() - amount)

    s = audio_manager.load_audio(VOLUME_DOWN_SOUND)
    audio_manager.play(s)
    audio_manager.block_while_playing()


def handle_card_random_song(card, audio_manager, uid):
    dir = card['random_song']

    all_files = os.listdir(dir)
    print(f"Found {len(all_files)} in {dir}...")
    only_wav_files = list()
    for file in all_files:
        if str(file).endswith(".wav"):
            only_wav_files.append(dir + file)

    idx = random.Random().randint(0, len(only_wav_files) - 1)
    file_to_play = only_wav_files[idx]
    print(f"Selected {file_to_play} out of {len(only_wav_files)} files.")

    snd = audio_manager.load_audio(file_to_play)
    audio_manager.play(snd)


def handle_card_file(card, audio_manager, uid):
    file = card['file']

    if isinstance(file, list):
        idx = random.Random().randint(0, len(file) - 1)
        file = file[idx]

    if os.path.exists(file):
        print(f"Playing: {file}")

        snd = audio_manager.load_audio(file)
        audio_manager.play(snd)
    else:
        print(f"File not found: {file}")


def main():
    audio_manager = audio.AudioManager.from_card_name(ALSA_CARD_NAME, ALSA_MIXER_NAME)

    while True:
        snd = random.Random().randint(0, len(STARTUP_SOUND) - 1)
        if os.path.exists(snd):
            seg = audio_manager.load_audio(STARTUP_SOUND[snd])
            audio_manager.play(seg)
            audio_manager.block_while_playing()
            break

    nfc = RC522Manager(lambda uid, card_on_reader: card_found_callback(audio_manager, uid, card_on_reader))

    try:
        while True:
            time.sleep(0.1)
    finally:
        audio_manager.shutdown()
        nfc.shutdown()


if __name__ == "__main__":
    main()
