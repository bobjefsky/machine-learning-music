'''
Author:     Ji-Sung Kim
Project:    deepjazz
Purpose:    Parse, cleanup and process data.

Code adapted from Evan Chow's jazzml, https://github.com/evancchow/jazzml with
express permission.
'''

from __future__ import print_function

from music21 import *
from collections import defaultdict, OrderedDict
#from itertools import groupby, izip_longest
from grammar import *

#----------------------------HELPER FUNCTIONS----------------------------------#

''' Helper function to parse a MIDI file into its measures and chords '''
#TODO: find the correct part where the melody is
def __parse_midi(data_fn):
    '''
    LOOKING TO MAKE THIS WORK WITH AND THEN I KNEW FROM SPOTIFY
    :param data_fn:
    :return:
    '''
    # Parse the MIDI data for separate melody and accompaniment parts.
    midi_data = converter.parse(data_fn) # type: music21.stream.Score

    # Get melody part, compress into single voice.
    melody_stream = midi_data[0]  # For Metheny piece, Melody is Part #5.

    #create a Voice object of rests, notes, and chords
    melody = stream.Part()
    for item in melody_stream:
        melody.append(item)

    for i in melody:
        if i.quarterLength == 0.0:
            i.quarterLength = 0.25

    # Change key signature to adhere to comp_stream (1 sharp, mode = major).
    # Also add Electric Guitar.
    #melody.insert(0, instrument.Piano()) # can get from melody_stream[0]
    #melody.insert(0, key.KeySignature(sharps=1)) # mode='major' removed

    # The accompaniment parts. Take only the best subset of parts from
    # the original data. Maybe add more parts, hand-add valid instruments.
    # Should add least add a string part (for sparse solos).
    # Verified are good parts: 0, 1, 6, 7 '''
    # Add Parts 0,1,6,7 from from midi_data # What makes them good?
    # These parts are good because their first element is an an Instrument such as piano, trumpet, horn
    # To see, look at midi_data then elements 0,1,6,7 and the first element in each of those
    #partIndices = [0, 1, 6, 7]
    #partIndices = [0]
    #comp_stream = stream.Voice()
    #comp_stream.append([j.flat for i, j in enumerate(midi_data)
        #if i in partIndices])

    # Full stream containing both the melody and the accompaniment.
    # All parts are flattened.
    full_stream = stream.Voice()
    # for i in range(len(comp_stream)):
    #     full_stream.append(comp_stream[i])
    full_stream.append(melody)

    # Extract solo stream, assuming you know the positions ..ByOffset(i, j).
    # Note that for different instruments (with stream.flat), you NEED to use
    # stream.Part(), not stream.Voice().
    # Accompanied solo is in range [478, 548) # How do we know this range? Is there even a solo in our files?
    # TODO: Cut out for loop but still flatten
    solo_stream = stream.Voice()
    # dont need a for looop because there is only 1 Part
    for part in full_stream:
        curr_part = stream.Part()
        curr_part.append(part.getElementsByClass(instrument.Instrument))
        curr_part.append(part.getElementsByClass(tempo.MetronomeMark))
        #curr_part.append(part.getElementsByClass(key.KeySignature))
        curr_part.append(part.getElementsByClass(meter.TimeSignature))
        curr_part.append(part.getElementsByOffset(3, len(part)-1, includeEndBoundary=True))
        cp = curr_part.flat
        solo_stream.insert(cp)

    # Group by measure so you can classify.
    # Note that measure 0 is for the time signature, metronome, etc. which have
    # an offset of 0.0.
    melody_stream = solo_stream[-1]  # last element of melody_stream
    measures = OrderedDict()
    offsetTuples = [(int(n.offset / 4), n) for n in melody_stream]
    measureNum = 0  # for now, don't use real m. nums (119, 120)
    for key_x, group in groupby(offsetTuples, lambda x: x[0]):
        measures[measureNum] = [n[1] for n in group]
        measureNum += 1

    # Get the stream of chords.
    # offsetTuples_chords: group chords by measure number.
    #chordStream = solo_stream[0]
    chordStream = solo_stream[0]
    chordStream.removeByClass(note.Rest)
    chordStream.removeByClass(note.Note)
    offsetTuples_chords = [(int(n.offset / 4), n) for n in chordStream]

    # Generate the chord structure. Use just track 1 (piano) since it is
    # the only instrument that has chords.
    # Group into 4s, just like before.
    chords = OrderedDict()
    measureNum = 0
    for key_x, group in groupby(offsetTuples_chords, lambda x: x[0]):
        chords[measureNum] = [n[1] for n in group]
        measureNum += 1

    # convert these chords to notes
    chord_type = chord.Chord()
    for index, inner_list in measures.items():
        inner_list_index = -1
        for item in inner_list:
            inner_list_index += 1
            if type(item) == type(chord_type):
                    new_note = note.Note(item.pitches[0].name)
                    print('putting ' + new_note.name + ' at ' + str(inner_list_index))
                    inner_list[inner_list_index] = new_note
                    #inner_list[current_index] = new_note
    # Fix for the below problem.
    #   1) Find out why len(measures) != len(chords).
    #   ANSWER: resolves at end but melody ends 1/16 before last measure so doesn't
    #           actually show up, while the accompaniment's beat 1 right after does.
    #           Actually on second thought: melody/comp start on Ab, and resolve to
    #           the same key (Ab) so could actually just cut out last measure to loop.
    #           Decided: just cut out the last measure.
    print(len(chords))
    print(len(measures))
    if(len(chords) != len(measures)): # shorter the longer one to the size of the smaller one
        del chords[len(chords) - 1]
    assert len(chords) == len(measures)

    return measures, chords

''' Helper function to get the grammatical data from given musical data. '''
def __get_abstract_grammars(measures, chords):
    # extract grammars
    abstract_grammars = []
    for ix in range(1, len(measures)):
        m = stream.Voice()
        for i in measures[ix]:
            m.insert(i.offset, i)
        c = stream.Voice()
        for j in chords[ix]:
            c.insert(j.offset, j)
            parsed = parse_melody(m, c)
        abstract_grammars.append(parsed)

    return abstract_grammars

#----------------------------PUBLIC FUNCTIONS----------------------------------#

''' Get musical data from a MIDI file '''
def get_musical_data(data_fn):
    measures, chords = __parse_midi(data_fn)
    abstract_grammars = __get_abstract_grammars(measures, chords)

    return chords, abstract_grammars

''' Get corpus data from grammatical data '''
def get_corpus_data(abstract_grammars):
    corpus = [x for sublist in abstract_grammars for x in sublist.split(' ')]
    values = set(corpus)
    val_indices = dict((v, i) for i, v in enumerate(values))
    indices_val = dict((i, v) for i, v in enumerate(values))

    return corpus, values, val_indices, indices_val