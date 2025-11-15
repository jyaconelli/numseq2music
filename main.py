import csv
import sys
from numbers2chords import get_hex, get_bits, hex_to_notes
from constants import BEATS_PER_ROW, NOTE_DURATIONS, NOTES_SHARP, NOTES_FLAT, MAJOR_SCALE_PATTERN, MINOR_SCALE_PATTERN, MAX_BPM, MIN_BPM
from Score import Score
from MidiUtils import make_midi, play_midi
from helpers import get_key_notes, scrape_oeis


def get_note_durations(total_duration, bits):
    temp_duration_unit = total_duration / len(bits)
    duration_unit = min(NOTE_DURATIONS, key=lambda d: abs(temp_duration_unit - d))

    all_bits = bits + bits[:max(0, int((BEATS_PER_ROW - (len(bits) * duration_unit)) // duration_unit))]
    note_durations = [0] * sum(all_bits)

    idx_pointer = -1
    for bit in all_bits:
        if bit == 1:
            idx_pointer += 1
        note_durations[idx_pointer] += duration_unit
    return note_durations


def resolve_moments(note_durations, notes):
    final_note_count = min(len(note_durations), len(notes))
    len_difference = abs(len(note_durations) - len(notes))

    if final_note_count < len(notes):  # Need more durations
        new_durations = [*note_durations]
        while len(new_durations) < len(notes):
            max_dur = max(new_durations)
            index = new_durations.index(max_dur)
            new_dur = max_dur / 2
            new_durations[index] = new_dur
            new_durations.insert(index, new_dur)
        return new_durations[:len(notes)], notes

    if final_note_count < len(note_durations):  # Need fewer durations
        new_durations = [*note_durations]
        for _ in range(len_difference):
            min_dur = min(new_durations)
            index = new_durations.index(min_dur)
            new_dur = new_durations.pop(index)
            if index < len(new_durations):
                new_durations[index] += new_dur
            else:
                new_durations[index - 1] += new_dur
        return new_durations, notes[:len(new_durations)]

    return note_durations, notes


def process_sequence(sequence, is_sharp=False):
    total = sum(sequence)
    root = NOTES_SHARP[total % len(NOTES_SHARP)] if '--sharp' in sys.argv else NOTES_FLAT[total % len(NOTES_FLAT)]
    mode = 'MAJOR' if total % 2 == 0 else 'MINOR'
    bpm = (total % (MAX_BPM - MIN_BPM)) + MIN_BPM
    print(f"Root: {root}, Mode: {mode}, BPM: {bpm}")
    key_notes, note_to_hex_dict, hex_to_note_dict = get_key_notes(root, mode, is_sharp)
    score = Score(root, hex_to_note_dict=hex_to_note_dict, note_to_hex_dict=note_to_hex_dict, mode=mode, tempo=bpm, is_sharp=is_sharp)

    first_note = (key_notes[bpm % len(key_notes)], 4)
    all_notes = NOTES_SHARP if is_sharp else NOTES_FLAT

    notes = [first_note]
    for num in sequence:
        bits = get_bits(num)
        hexs = get_hex(num)
        note_durations = get_note_durations(BEATS_PER_ROW, bits)

        for h in hexs:
            notes += hex_to_notes(h, note_to_hex_dict.get(notes[-1][0]), octave=4,
                                  hex_to_note_dict=hex_to_note_dict, note_to_hex_dict=note_to_hex_dict, notes=all_notes)

        new_durs, new_notes = resolve_moments(note_durations, notes)
        score.add_phrase(new_durs, new_notes)
        notes = [new_notes[-1]]
    score.generate_chords()
    return score


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python3 main.py <inputfile> <optional outputfile> <optional -p or --play for play>")
        sys.exit(1)

    input_file = sys.argv[1]
    seq = []

    if input_file.endswith('.csv'):
        with open(input_file) as csvf:
            reader = csv.reader(csvf)
            seq = [int(row[0]) for row in reader if int(row[0]) != 0]
    else:
        seq = [n for n in scrape_oeis(input_file) if n > 0]

    bpm = 90
    total = sum(seq)
    bpm = (total % (MAX_BPM - MIN_BPM)) + MIN_BPM
    ROOT = NOTES_SHARP[total % len(NOTES_SHARP)] if '--sharp' in sys.argv else NOTES_FLAT[total % len(NOTES_FLAT)]
    MODE = 'MAJOR' if total % 2 == 0 else 'MINOR'

    score = process_sequence(seq, is_sharp=False)

    if len(sys.argv) == 3:
        if sys.argv[2] == '-p' or sys.argv[2] == '--play':
            print('playing score...')
            play_midi(score)
        else:
            output_file = sys.argv[2]
            make_midi(score, output_file)
            print(f"Saved score to {output_file}")
    elif len(sys.argv) == 4 and sys.argv[3] in ('-p', '--play'):
        print('playing score...')
        play_midi(score)
