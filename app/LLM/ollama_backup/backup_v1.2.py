import sys
import subprocess
import threading
import queue
import re
import asyncio
import edge_tts
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from personality.friday_personality import personality
import emoji

class FridayAssistant:
    def __init__(self, model_name="llama3.2:1b", temperature=0.5, voice="en-US-JennyNeural", rate="+20%"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        self.voice = voice
        self.rate = rate
        self.sentence_queue = queue.Queue()
        self.ffplay_proc = None
        self.audio_thread = None

    def start_audio_worker(self):
        """Starts the background audio processing and ffplay subprocess."""
        self.ffplay_proc = subprocess.Popen(
            ["ffplay", "-autoexit", "-nodisp", "-i", "pipe:0"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        async def process_sentences():
            while True:
                try:
                    sentence = await asyncio.to_thread(self.sentence_queue.get, True, 0.1)
                except queue.Empty:
                    await asyncio.sleep(0.05)
                    continue

                if sentence is None:
                    break
                    
                clean_sentence = sentence.strip()
               
                clean_sentence = emoji.replace_emoji(clean_sentence, replace="").strip()
                if clean_sentence:
                    communicate = edge_tts.Communicate(clean_sentence, self.voice, rate=self.rate)
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            self.ffplay_proc.stdin.write(chunk["data"])
                            self.ffplay_proc.stdin.flush()
                self.sentence_queue.task_done()
                
        def worker_thread():
            asyncio.run(process_sentences())
            self.ffplay_proc.stdin.close()
            self.ffplay_proc.wait()

        self.audio_thread = threading.Thread(target=worker_thread, daemon=True)
        self.audio_thread.start()

    def stop_audio_worker(self):
        """Cleanly stops the background audio worker."""
        if self.audio_thread and self.audio_thread.is_alive():
            self.sentence_queue.put(None)
            self.audio_thread.join()

    def chat(self, user_prompt):
        """Streams the LLM response for a single user prompt."""
        messages = [
            SystemMessage(content=personality),
            HumanMessage(content=user_prompt)
        ]

        print("AI: ", end="", flush=True)
        
        buffer = ""
        for chunk in self.llm.stream(messages):
            text = chunk.content
            print(text, end="", flush=True)
            buffer += text
            
            # Check for sentence boundaries including commas and colons
            match = re.search(r'(?<=[.,!?:;])[\s\n]+', buffer)
            if match:
                split_idx = match.end()
                sentence = buffer[:split_idx]
                self.sentence_queue.put(sentence)
                buffer = buffer[split_idx:]

        if buffer.strip():
            self.sentence_queue.put(buffer.strip())

        print()

    def interactive_loop(self):
        """Runs a continuous chat loop."""
        print("Starting Friday Assistant... (Type 'quit' or 'exit' to stop)")
        self.start_audio_worker()
        try:
            while True:
                user_prompt = input("\nYOU : ")
                if user_prompt.lower() in ["quit", "exit", "stop"]:
                    break
                self.chat(user_prompt)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.stop_audio_worker()

if __name__ == "__main__":
    assistant = FridayAssistant()
    assistant.interactive_loop()