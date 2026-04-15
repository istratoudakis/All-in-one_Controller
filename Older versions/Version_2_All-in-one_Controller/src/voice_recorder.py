import pyaudio
import wave
import os

class VoiceRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000 
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False
        
        self.temp_dir = "temp_audio"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=1,  # <--- Κλειδωμένο στο ID σου
                frames_per_buffer=self.chunk
            )
            print("\n--- Recording Started (Using ID 1) ---")
        except Exception as e:
            print(f"Mic Error: {e}")

    def record_chunk(self):
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except:
                pass

    def stop_recording(self):
        if not self.is_recording: return None
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        file_path = os.path.join(self.temp_dir, "command.wav")
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return file_path