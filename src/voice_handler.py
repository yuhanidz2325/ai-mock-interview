"""
Voice Handler Module - Browser-based Audio Recording
Menggunakan browser microphone via streamlit_mic_recorder
"""

import io
import tempfile
import os


class VoiceHandler:
    """
    Handles voice recording and speech-to-text transcription
    Menggunakan browser microphone (no PyAudio needed!)
    """
    
    def __init__(self):
        # Check if SpeechRecognition available
        self.voice_available = False
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.voice_available = True
        except ImportError:
            self.recognizer = None
    
    def transcribe_from_audio_bytes(self, audio_bytes):
        """
        Transcribe audio dari bytes yang direkam browser
        
        Args:
            audio_bytes: Audio data dalam bytes (dari mic recorder)
            
        Returns:
            str: Transcribed text atau error message
        """
        if not self.voice_available:
            return """❌ Library SpeechRecognition belum terinstall!

Install dengan:
pip install SpeechRecognition

Kemudian restart aplikasi.
"""
        
        if not audio_bytes:
            return "❌ Tidak ada audio yang direkam. Coba lagi."
        
        try:
            import speech_recognition as sr
            
            # Save audio bytes to temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_audio_path) as source:
                    audio_data = self.recognizer.record(source)
                
                # Transcribe menggunakan Google Speech Recognition (Bahasa Indonesia)
                text = self.recognizer.recognize_google(audio_data, language='id-ID')
                
                return text
                
            finally:
                # Cleanup temporary file
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            
        except sr.UnknownValueError:
            return """❌ Tidak dapat memahami audio yang direkam.

Tips:
- Bicara lebih jelas dan keras
- Pastikan tidak ada background noise
- Rekam di tempat yang tenang
- Coba rekam ulang"""
        
        except sr.RequestError as e:
            return f"""❌ Error koneksi ke Google Speech API: {str(e)}

Pastikan:
- Anda terkoneksi internet
- Koneksi stabil (tidak putus-putus)
- Coba lagi dalam beberapa saat"""
        
        except Exception as e:
            return f"""❌ Error saat memproses audio: {str(e)}

Coba:
- Rekam ulang audio
- Pastikan audio tidak corrupt
- Restart aplikasi jika masih error"""
    
    def get_setup_instructions(self):
        """
        Return instruksi setup untuk mode suara
        """
        return """
### 🎤 Setup Mode Suara

Mode suara sekarang menggunakan **browser microphone** - jauh lebih mudah!

#### Install (Hanya 1 Command):

```bash
pip install streamlit-mic-recorder SpeechRecognition
```

#### Restart Aplikasi:

```bash
streamlit run app.py
```

Setelah itu mode suara langsung bisa digunakan! 🚀

#### Cara Pakai:

1. Klik tombol **"🔴 Rekam"**
2. Browser akan minta izin microphone - **Allow/Izinkan**
3. Bicara jawaban Anda dalam **Bahasa Indonesia**
4. Klik **"⏹️ Stop"** jika selesai
5. Dengar playback (opsional)
6. Klik **"📝 Transkripsi"**
7. Edit jika perlu, lalu **Analisis**!

#### Troubleshooting:

**Browser tidak minta izin microphone?**
- Cek Settings browser → Permissions → Microphone
- Pastikan localhost diizinkan

**Transkripsi salah?**
- Bicara lebih jelas dan keras
- Rekam di tempat tenang
- Gunakan headset dengan mic jika ada

**Tidak ada suara saat playback?**
- Cek volume speaker/headphone
- Browser mungkin mem-block autoplay
"""
    
    def provide_voice_mode_guide(self):
        """
        Panduan lengkap mode suara
        """
        guide = """
## 🎤 Panduan Mode Suara

### Persiapan:
1. ✅ Pastikan microphone terhubung (built-in laptop juga OK)
2. ✅ Cari tempat yang tenang
3. ✅ Siapkan jawaban (pikirkan struktur STAR)
4. ✅ Test volume microphone

### Saat Merekam:
- 🎯 Bicara dengan jelas dalam Bahasa Indonesia
- 🎯 Kecepatan normal (tidak terlalu cepat/lambat)
- 🎯 Ucapkan istilah teknis dengan jelas
- 🎯 Jeda sebentar antar kalimat
- 🎯 Durasi ideal: 2-3 menit

### Istilah Teknis:

| Istilah | Cara Bicara |
|---------|-------------|
| SQL | "es-ku-el" (eja huruf) |
| API | "a-pe-i" atau "application programming interface" |
| ML | "em-el" atau "machine learning" |
| pandas | "pan-das" (seperti hewan panda) |
| scikit-learn | "scikit learn" (jelas pisahkan) |

### After Recording:
1. ✅ Dengar playback untuk cek kualitas
2. ✅ Jika jelek, rekam ulang
3. ✅ Klik transkripsi
4. ✅ Edit hasil jika ada salah
5. ✅ Analisis seperti biasa

### Tips Pro:
- 📱 Gunakan headset dengan mic untuk kualitas lebih baik
- 🔇 Matikan notifikasi & tutup aplikasi berisik
- ⏱️ Latihan dulu tanpa rekam untuk flow yang smooth
- 📝 Buat bullet points sebelum bicara
"""
        
        return guide
