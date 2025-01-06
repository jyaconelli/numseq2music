import csv
import sys
from numbers2chords import get_hex, get_bits, hex_to_notes
from constants import BEATS_PER_ROW, NOTE_DURATIONS, NOTES_SHARP, NOTES_FLAT, MAJOR_SCALE_PATTERN, MINOR_SCALE_PATTERN, MAX_BPM, MIN_BPM
from Score import Score
from MidiUtils import make_midi, play_midi
from helpers import get_key_notes, scrape_oeis

ROOT = 'B'
MODE = 'MINOR'
is_sharp = False

def get_note_durations(total_duration, bits):
    total_notes = sum(bits)
    temp_duration_unit = total_duration / len(bits)
    duration_unit = 0
    min_dist = float('inf')
    for d in NOTE_DURATIONS:
        dist = abs(temp_duration_unit - d)
        if dist < min_dist:
            min_dist = dist
            duration_unit = d

    all_bits = bits

    # add bits if necessary
    remaining_size = BEATS_PER_ROW - (len(bits)*duration_unit)
    bits_needed = 0
    if remaining_size > 0:
        bits_needed = remaining_size / duration_unit
    all_bits = bits + bits[:int(bits_needed)]
    total_notes += sum(bits[:int(bits_needed)])
    
    # remove bits if necessary
    if remaining_size < 0:
        bits_to_remove = remaining_size / duration_unit
        all_bits = all_bits[:int(bits_to_remove)]
        total_notes = sum(all_bits)
    note_durations = [0]*total_notes

    idx_pointer = -1 # so first one bumps to 0
    for bit in all_bits:
        if bit == 1:
            idx_pointer += 1
        note_durations[idx_pointer] += duration_unit
    return note_durations


def resolve_moments(note_durations, notes):
    if len(note_durations) == len(notes):
        return (note_durations, notes)
    final_note_count = min(len(note_durations), len(notes))
    len_difference = max(len(note_durations), len(notes)) - final_note_count

    if final_note_count < len(notes): # i.e. we need to add more durations
        new_notes = [*notes]
        new_durations = [*note_durations]
        for _ in range(len_difference): # repeatedly split the max value in half
            max_dur = max(new_durations)
            index = new_durations.index(max_dur)
            new_dur = max_dur / 2.
            new_durations[index] = new_dur
            new_durations.insert(index, new_dur)
        return (new_durations, new_notes)

    if final_note_count < len(note_durations): # i.e. we need to remove some durations
        new_notes = [*notes]
        new_durations = [*note_durations]
        sorted_durs = [*new_durations]
        sorted_durs.sort()
        for _ in range(len_difference):
            index = -1
            while index == -1:
                sorted_durs = [*new_durations]
                sorted_durs.sort()
                min_dur = sorted_durs.pop(0)
                try:
                    index = new_durations.index(min_dur)
                except:
                    index = -1
            new_dur = new_durations.pop(index)
            if index < len(new_durations) - 2:
                new_durations[index] += new_dur
            else:
                new_durations[index-1] += new_dur
        return (new_durations, new_notes)
    return (note_durations, notes)


if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage: python3 main.py <inputfile> <optional outputfile> <optional -p or --play for play>")

input_file = sys.argv[1]
seq = []

if input_file.endswith('.csv'):
    with open(input_file) as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            num = int(row[0])
            if num != 0:
                seq.append(int(row[0]))
else:
    seq_dirty = scrape_oeis(input_file)
    for n in seq_dirty:
        if n > 0:
            seq.append(n)

bpm = 90
first_note = None
total = 0
for num in seq:
    total += num
ROOT_idx = total % len(NOTES_SHARP)
ROOT = NOTES_SHARP[ROOT_idx] if is_sharp else NOTES_FLAT[ROOT_idx]
MODE = 'MAJOR' if total % 2 == 0 else 'MINOR'
print(f"KEY = {ROOT} {MODE}")
key_notes, note_to_hex_dict, hex_to_note_dict = get_key_notes(ROOT, MODE, is_sharp)
bpm = (total % (MAX_BPM - MIN_BPM)) + MIN_BPM
first_note = (key_notes[(total + bpm) % len(key_notes)], 4)
print(first_note)

key_notes, note_to_hex_dict, hex_to_note_dict = get_key_notes(ROOT, MODE, is_sharp)
score = Score(ROOT, hex_to_note_dict=hex_to_note_dict, note_to_hex_dict=note_to_hex_dict, mode=MODE, tempo=bpm, is_sharp=is_sharp)
all_notes = NOTES_SHARP if is_sharp else NOTES_FLAT
print(f"BPM: {bpm}")

bads = 0
for num in seq:
    bits = get_bits(num)
    hexs = get_hex(num)
    note_durations = get_note_durations(BEATS_PER_ROW, bits)
    notes = [first_note]
    for h in hexs:
        notes += hex_to_notes(h, note_to_hex_dict.get(notes[-1][0]), octave=4, hex_to_note_dict=hex_to_note_dict, note_to_hex_dict=note_to_hex_dict, notes=all_notes)

    # resolve note_durations and notes length mismatch
    new_durs, new_notes = resolve_moments(note_durations, notes)
    if sum(new_durs) != 64:
        bads += 1
    score.add_phrase(new_durs, new_notes)
score.describe()
# print(score)
score.generate_chords()
chord_str = ''
chord_counter = 0
for c in score.chords:
    chord_str += str(c) + '\t'
    chord_counter += 1
    if chord_counter % 4 == 0:
        chord_str += '\n'
        if chord_counter > 5*4:
            chord_str += '...'
            break
print(chord_str)
if len(sys.argv) == 3:
    if sys.argv[2] == '-p' or sys.argv[2] == '--play':
        play_midi(score)
    else:
        output_file = sys.argv[2]
        make_midi(score, output_file)
        print(f"Saved score to {output_file}")
if len(sys.argv) == 4:
    if sys.argv[3] == '-p' or sys.argv[3] == '--play':
      play_midi(score)
    

        

