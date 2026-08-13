import asyncio
import edge_tts
import subprocess
import time

async def main():
    ffplay_proc = subprocess.Popen(
        ["ffplay", "-autoexit", "-nodisp", "-i", "pipe:0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    for text in ["Hello one.", "Hello two.", "Hello three."]:
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffplay_proc.stdin.write(chunk["data"])
                ffplay_proc.stdin.flush()
        print(f"Sent: {text}")
        time.sleep(1) # simulate time gap
        
    ffplay_proc.stdin.close()
    ffplay_proc.wait()

asyncio.run(main())
