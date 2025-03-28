import yt_dlp
import whisper
import os
from youtube_transcript_api import YouTubeTranscriptApi
import nltk
from deepmultilingualpunctuation import PunctuationModel # Ensure you have a punctuation model installed

# Initialize the punctuation model

class Transcript:

    def __init__(self):
        self.punctuation_model = PunctuationModel()  # Load punctuation model
        self.whisper_model = whisper.load_model("base")


    def get_transcript(self, video_url: str) -> str:
        try:
            video_id = video_url.split("v=")[-1]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript])
        except:
            return False
        
    # :one: Download Audio
    def download_audio(self, youtube_url:str, output_file:str ="audio.mp3"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            
    # :two: Transcribe using Whisper
    def transcribe_audio(self, audio_file):
        result = self.whisper_model.transcribe(audio_file)
        return result["text"]


    def needs_punctuation(self, text: str, threshold: float = 0.02) -> bool:
        """Check if text needs punctuation based on the percentage of punctuated sentences."""
        punctuation_marks = {'.', ',', '?', '!'}
        punctuated_count = sum(1 for char in text if char in punctuation_marks)
        total_chars = len(text)
        return (punctuated_count / total_chars) < threshold


    def format_transcript(self, text:str) -> str:
        """Format transcript into well-structured sentences using PunctuationModel."""
        # Apply auto-punctuation if needed
        if self.needs_punctuation(text):
            text = self.punctuation_model.restore_punctuation(text)
        # Split into proper sentences
        sentences = nltk.tokenize.sent_tokenize(text)
        # Structure into paragraphs (every 5 sentences make a new paragraph)
        structured_text = "\n\n".join([" ".join(sentences[i:i+5]) for i in range(0, len(sentences), 5)])
        return structured_text


    def Transcript(self, link:str) -> str:
        youtube_url = link
        text = self.get_transcript(youtube_url)
        if(text):
            text_output=text
        else:
            self.download_audio(youtube_url, "audio.mp3")
            text_output = self.transcribe_audio("audio.mp3")
            os.remove("audio.mp3")
        
        return self.format_transcript(text_output)

transcript_process = Transcript()