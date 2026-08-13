import subprocess
import sys

sentence = "This is a test of edge tts."
print("Running edge-tts...")
edge_proc = subprocess.Popen(
    [sys.executable, "-m", "edge_tts", "--text", sentence],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)
ffplay_proc = subprocess.Popen(
    ["ffplay", "-autoexit", "-nodisp", "-i", "pipe:0"],
    stdin=edge_proc.stdout,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
edge_proc.stdout.close()
ffplay_proc.communicate()
print("Done!")
