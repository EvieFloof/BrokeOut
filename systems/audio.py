"""
audio - Moteur audio de BrokeEngine

EwoFluffy - BrokeTeam - 2025
"""

import threading
import wave
from dataclasses import dataclass
from queue import Queue
from typing import Dict

import numpy as np
import sounddevice as sd

from systems.config import config
from systems.logging import Logger


class Reverb:
    """
    Reverb - Réverbe basée sur un modèle Schroeder
    Volontairement simplifié, mais suffisant pour donner de l'immersion.
    """

    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.delay = int(0.03 * sample_rate)
        self.buffer = np.zeros(self.delay, dtype=np.float32)
        self.index = 0

    def process(self, stereo: np.ndarray, amount: float):
        if amount <= 0.0:
            return stereo

        mono = stereo.mean(axis=0)
        out = np.zeros_like(stereo)

        for i in range(mono.size):
            delayed = self.buffer[self.index]
            self.buffer[self.index] = mono[i] + delayed * 0.6
            mix = mono[i] * (1 - amount) + delayed * amount
            out[0, i] = mix
            out[1, i] = mix
            self.index = (self.index + 1) % self.delay

        return out


class Distortion:
    """
    Distortion - Simule vaguement (À retravailler) une saturation douce
    en utilisant une fonction tanh.
    """

    def process(self, stereo: np.ndarray, drive_db: float):
        if drive_db <= 0.0:
            return stereo

        gain = 10 ** (drive_db / 20)
        boosted = stereo * gain
        return np.tanh(boosted)


class Chorus:
    """
    Chorus - Chorus simple utilisant un délai modulé.
    Inspiré d'un modèle de chorus analogiques de base : LFO (Oscillateur basses fréquences) → délai → mix.
    """

    def __init__(self, sample_rate: int):
        self.sr = sample_rate
        self.max_delay = int(0.02 * sample_rate)
        self.buffer_l = np.zeros(self.max_delay, dtype=np.float32)
        self.buffer_r = np.zeros(self.max_delay, dtype=np.float32)
        self.index = 0
        self.phase = 0.0

    def process(self, stereo: np.ndarray, amount: float):
        if amount <= 0.0:
            return stereo

        out = np.zeros_like(stereo)
        rate = 0.3

        for i in range(stereo.shape[1]):
            self.buffer_l[self.index] = stereo[0, i]
            self.buffer_r[self.index] = stereo[1, i]

            mod = (np.sin(self.phase) + 1) * 0.5
            delay = int(mod * self.max_delay)

            read = (self.index - delay) % self.max_delay
            out[0, i] = (stereo[0, i] + self.buffer_l[read] * amount) / 2
            out[1, i] = (stereo[1, i] + self.buffer_r[read] * amount) / 2

            self.index = (self.index + 1) % self.max_delay
            self.phase += (2 * np.pi * rate) / self.sr

        return out


class Lowpass:
    """
    Lowpass - Filtre passe-bas très simple.
    Pour enlever les aigus ou simuler un effet de distance.
    """

    def __init__(self, sample_rate: int):
        self.sr = sample_rate
        self.prev = np.zeros(2, dtype=np.float32)

    def process(self, stereo: np.ndarray, cutoff: float):
        if cutoff >= 20000.0:  # 20 KHz, inutile d'appliquer l'effet
            return stereo

        rc = 1.0 / (2 * np.pi * cutoff)
        dt = 1.0 / self.sr
        alpha = dt / (rc + dt)
        out = np.zeros_like(stereo)

        for i in range(stereo.shape[1]):
            self.prev = self.prev + alpha * (stereo[:, i] - self.prev)
            out[:, i] = self.prev  # Toutes les lignes, colone i

        return out


@dataclass
class AudioEffect:
    """
    AudioEffect - Classe qui stocke les valeurs des effets audios
    """

    reverb: float = 0.0
    distortion: float = 0.0
    chorus: float = 0.0
    lowpass: float = 20000


class AudioEngine:
    """
    AudioEngine - Moteur audio de BrokeEngine (version sans Pedalboard)
    """

    def __init__(self, sample_rate=48000, block_size=512):
        self.logger = Logger("systems.audio")

        self.sample_rate = sample_rate
        self.block_size = block_size
        self.sounds: Dict[str, np.ndarray] = {}
        self.playing_sounds = []
        self.stream = None

        self.effects = AudioEffect()

        self.reverb = Reverb(sample_rate)
        self.distortion = Distortion()
        self.chorus = Chorus(sample_rate)
        self.lowpass = Lowpass(sample_rate)

        self.lock = threading.Lock()
        self.command_queue = Queue()

        self.audio_thread = None
        self.running = False

        self.threads = {}

    def load_sound(self, name: str, filepath: str):
        try:
            with wave.open("assets/sounds/" + filepath, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                audio /= 32768.0  # Normalisation de l'audio

                if wf.getnchannels() == 1:
                    audio = np.stack([audio, audio])
                else:
                    audio = audio.reshape(-1, 2).T

                with self.lock:
                    self.sounds[name] = audio

                self.logger.log(f"Loaded sound: {name}")
                return True

        except Exception as e:
            self.logger.error(f"Error loading {name}: {e}")
            return False

    def play_sound(self, name: str, loop=False, volume=config.audio.volume.master):
        if name not in self.sounds:
            self.logger.error(f"Sound doesn't exists: {name}")
            return

        with self.lock:
            self.playing_sounds.append(
                {"data": self.sounds[name] * volume, "position": 0, "loop": loop}
            )

    def stop_all(self):
        with self.lock:
            self.playing_sounds.clear()

    def audio_callback(self, outdata, frames, time_info, status):
        if status:
            self.logger.warn(f"Audio status: {status}")

        mixed = np.zeros((2, frames), dtype=np.float32)

        with self.lock:
            for sound in self.playing_sounds[:]:
                data = sound["data"]
                pos = sound["position"]
                remain = data.shape[1] - pos

                if remain <= 0:
                    if sound["loop"]:
                        sound["position"] = 0
                        continue
                    else:
                        self.playing_sounds.remove(sound)
                        continue

                to_copy = min(frames, remain)
                mixed[:, :to_copy] += data[:, pos : pos + to_copy]
                sound["position"] += to_copy

        x = mixed
        x = self.distortion.process(x, self.effects.distortion)
        x = self.chorus.process(x, self.effects.chorus)
        x = self.reverb.process(x, self.effects.reverb)
        x = self.lowpass.process(x, self.effects.lowpass)

        x = np.clip(x, -1.0, 1.0)
        outdata[:] = x.T

    def start(self):
        if self.running:
            self.logger.warn("Audio engine already running")
            return

        self.running = True
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=2,
            callback=self.audio_callback,
        )
        self.stream.start()
        self.logger.success("Audio engine successfully initialized")

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.logger.log("Audio engine stopped")

    def set_reverb(self, amount: float):
        self.effects.reverb = max(0.0, min(1.0, amount))
        self.logger.log(f"Reverb effect set to {amount}")

    def set_distortion(self, amount: float):
        self.effects.distortion = max(0.0, min(40.0, amount))
        self.logger.log(f"Distrortion effect set to {amount}")

    def set_chorus(self, amount: float):
        self.effects.chorus = max(0.0, min(1.0, amount))
        self.logger.log(f"Chorus effect set to {amount}")

    def set_lowpass(self, frequency: float):
        self.effects.lowpass = max(20.0, min(20000.0, frequency))
        self.logger.log(f"Lowpass effect set to {frequency}")

    def fade_reverb(self, target: float, duration: float):
        def _fade():
            start = self.effects.reverb
            steps = int(duration * 60)
            for i in range(steps):
                t = i / steps
                self.effects.reverb = start + (target - start) * t
                threading.Event().wait(duration / steps)

        self.threads["Reverb"] = threading.Thread(target=_fade, daemon=True).start()

    def fade_lowpass(self, target: float, duration: float):
        def _fade():
            start = self.effects.lowpass
            steps = int(
                duration * 60
            )  # 60 étapes par secondes (Aucun rapport avec les FPS graphiques)
            for i in range(steps):
                t = i / steps
                self.effects.lowpass = start + (target - start) * t
                threading.Event().wait(duration / steps)

        self.threads["Lowpass"] = threading.Thread(target=_fade, daemon=True).start()
