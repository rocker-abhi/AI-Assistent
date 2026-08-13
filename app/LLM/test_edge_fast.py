import asyncio
import edge_tts
import subprocess
import time

async def main():
    start = time.time()
    communicate = edge_tts.Communicate("Hello there, this is a much faster way to do text to speech.", "en-US-AriaNeural")
    
    ffplay_proc = subprocess.Popen(
        ["ffplay", "-autoexit", "-nodisp", "-i", "pipe:0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    first = True
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            if first:
                print(f"Time to first audio byte: {time.time() - start:.3f}s")
                first = False
            ffplay_proc.stdin.write(chunk["data"])
            ffplay_proc.stdin.flush()
            
    ffplay_proc.stdin.close()
    ffplay_proc.wait()

asyncio.run(main())
