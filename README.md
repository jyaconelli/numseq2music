





# numseq2music

Python tools for turning integer sequences into playable and savable MIDI sketches. This README focuses exclusively on the command-line workflow that lives under main.py and the supporting Python modules (numbers2chords.py, Score.py, MidiUtils.py, etc.). The browser UI and ui.py are intentionally out of scope here.

## Requirements

Python 3.9+ (tested locally with CPython).

System audio stack that pygame can talk to (macOS CoreAudio, PulseAudio/ALSA on Linux, etc.).

Dependencies from requirements.txt:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pygame needs SDL libraries. On Linux, install libsdl2-dev (or distro equivalent) before pip install.

## Data Sources

main.py expects positive integers and will automatically drop zeros. You can feed that data in two ways:

CSV file – Any .csv whose first column is integers. Example files such as numbers.csv and numbers2.csv are included.

OEIS sequence code – Pass an OEIS ID like A000045. The script downloads the sequence via helpers.scrape_oeis and uses the resulting list.

## CLI Usage

python main.py &lt;input&gt; [output_file] [-p | --play]
&lt;input&gt;: path to a CSV file (preferred) or an OEIS sequence ID.

output_file (optional): where to write the generated MIDI. If omitted, no file is written—useful for quick experiments that only need playback.

-p / --play (optional): renders a temporary MIDI (tempfile_forplay.midi) and plays it immediately through pygame.

### Common command patterns

# Render numbers.csv to a MIDI file
python main.py numbers.csv output.mid

# Fetch Fibonacci numbers from OEIS and save while also auditioning
python main.py A000045 fib.mid --play

# Just listen to the generated score without writing a file
python main.py numbers2.csv -p
If you provide both output_file and --play, the file is written first (output_file) and the same Score instance is then handed to play_midi.

## What the CLI Does

Key/tempo selection – The sum of the sequence decides the key root, mode (major/minor), and BPM within [80, 140].

Bit + hex conversion – Each number becomes both binary (get_bits) for rhythm shaping and hexadecimal (get_hex) for melodic movement.

Phrase construction – get_note_durations and resolve_moments align durations with generated notes; Score.add_phrase stores each moment.

Harmony generation – After all phrases, Score.generate_chords scans each measure’s melodic content and chooses the closest diatonic chord (with simple inversions to avoid long repeats).

Export / playback – MidiUtils.make_midi writes two tracks (melody + chords) via midiutil, and play_midi optionally streams it through pygame.

## File Tour (Python CLI only)

main.py – argument parsing, IO, orchestration.

numbers2chords.py – helpers that transform numbers into note names by mapping hex digits to the current key.

Score.py – Score, Note, and Chord classes plus the chord-selection heuristics.

MidiUtils.py – MIDI writer and audio playback helper.

helpers.py – OEIS scraping and key-generation utilities.

constants.py – tweakable musical constants such as BPM limits, note durations, and scale patterns.

## Troubleshooting

No sound on --play – Ensure the system audio device is free and that pygame initialized successfully (the script prints Python exceptions if audio fails).

OEIS downloads fail – The CLI needs outbound HTTPS access. Retry later or supply a CSV instead.

Empty output – Remember to pass an output filename; otherwise nothing is saved to disk.

## 



# Thoughts and Ideas

bloom filter but set 0s too, use as sine waves to combine (0th=sine, 1st=sine*2^1, 2nd=sine*2^2… ith=sine*2^i) for evolving tone. Alternatively, use traditional filter for only growing noise sine wave

instead of messing w/ hex, how about convert to base7 and then that becomes the notes?

then you could use base16 or something else… chords…?

base10 int to arbitrary base helper func

def numberToBase(n, b):
if n == 0:
    return [0]
digits = []
while n:
    digits.append(int(n % b))
    n //= b
return digits[::-1]
need to encourage runs more (maybe not… listen to A266069)

repetition / global structure needs to be created &amp; enforced

along with some basic harmonic rules, i.e. end on the tonic? but also this is technically a “never done” composition

maybe somehow the numbers themselves also inform structure… like order # 324 adds to the composition and also creates the sequence of segments 3, 2, and 4. Or 3 % &lt;# of parts&gt;, 2 % &lt;# of parts&gt;, 4 % &lt;# of parts&gt; or something… or just use

need some way maybe to occassionally change the BEATS_PER_LINE? Or some other way to vary order (magnitude) of note sizes. i.e from 64 to 32 for faster part ,or 128 for slower sections. This also can come from large and small numbers, which via resolution will lead to fast/slow sections

✅ need to enforce time signature / measures better. even with splitting or truncating phrases or something.

However, the added rhythmic complexity of allowing to cross measure boundaries is nice and don’t totally want to lose that

maybe splitting notes and doubling over phrases is better, and then let midi resolution merge

or, alternatively, just force chords to stick to measures which could give better coherence

instead of doing all chords for 1 measure, lets say if the distance to closest chord is &gt; some cutoff X,break the measure into two chords. This could be recursive, and X would scale the pace of chords (max 1 meaasure still)

Maybe blend chords that are repeated instead of going inversions? Idk… Inversions are cool too

the motifs that emerge are incredible interesting… so cool… what in the sequence/numbers makes this happen??



