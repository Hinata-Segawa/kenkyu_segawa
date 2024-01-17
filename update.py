from music21 import *
import itertools
import numpy as np
from xmlRead import *
from HMM import *

#適用させた結果から，新しい配列に音符の押弦位置と休符を入れる
def init_new_noteAndRest(new_noteAndRest,notes,res):
    count = 0
    # 休符は-1にして新しく配列に入れる
    for i in range(len(notes)):
        if notes[i].isNote:
            new_noteAndRest.append(res[count])
            count += 1
        else:
            new_noteAndRest.append(-1)

# 16分音符でもそのまま変換
def update_note(notes, new_noteAndRest,frets_items):
    for i in range(len(notes)):
        if notes[i].isNote:
            notes[i].articulations = [articulations.StringIndication(new_noteAndRest[i] % 6+1), 
                                      articulations.FretIndication(new_noteAndRest[i]//6)]

            # 新しい押弦位置のpitchに更新
            p = frets_items[new_noteAndRest[i]][0]
            notes[i].pitch = pitch.Pitch(p)


#四分音符に変換する関数
def create_new_note(old_note, new_noteAndRest_index):
    new_note = note.Note(old_note.pitch)
    new_note.duration = duration.Duration(1.0)  # 4分音符のdurationは1.0
    new_note.articulations = [articulations.StringIndication(new_noteAndRest_index % 6+1),
                              articulations.FretIndication(new_noteAndRest_index//6)]
    return new_note


#八分音符に変換する関数
def create_new_note_eighth(old_note, new_noteAndRest_index):
    new_note = note.Note(old_note.pitch)
    new_note.duration = duration.Duration(0.5)  # 8分音符のdurationは0.5
    new_note.articulations = [articulations.StringIndication(new_noteAndRest_index % 6+1),
                              articulations.FretIndication(new_noteAndRest_index//6)]
    return new_note



#八分音符三連続の時に付点八分音符に変える
def create_augmentOrDiminish(old_note, new_noteAndRest_index):
    new_note = note.Note(old_note.pitch)
    new_note.duration.type = 'eighth'  
    new_note.duration.dots = 1
    new_note.articulations = [articulations.StringIndication(new_noteAndRest_index % 6+1),
                              articulations.FretIndication(new_noteAndRest_index//6)]
    
    return new_note



# 8分音符2連続なら，16分音符4連続なら変換
def update_note_quarter(notes, new_noteAndRest,down_up):
    """
    音符のリストを受け取り、16分音符と8分音符の連続を四分音符に変換した新しい音符のリストを返す関数
    """
    new_notes = []
    i = 0

    while i < len(notes):


        if isinstance(notes[i], note.Rest):
            # 元の音符が休符の場合、そのまま新しいリストに追加
            new_notes.append(notes[i])
            i += 1
            if i + 2 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.25 for n in notes[i:i+3]):
                if all(n == -1 for n in down_up[i:i+3]):
                    new_notes.append(create_augmentOrDiminish(notes[i],new_noteAndRest[i]))
                    i += 3
        elif i + 3 < len(notes) and all(n.duration.quarterLength == 0.25 for n in notes[i:i+4]):
            # 16分音符が4つ連続しているかチェック
            if down_up[i] == 1 and isinstance(notes[i],note.Note):
                new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
                i += 4
            else:
                new_notes.append(notes[i])
                i += 1

        elif i + 1 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.5 for n in notes[i:i+2]):
            # 8分音符が2つ連続しているかチェック
            if down_up[i] == 1:
                new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
                i += 2
            else:
                new_notes.append(notes[i])
                i += 1
        elif i + 2 < len(notes) and all(isinstance(n, note.Note) for n in notes[i:i+3]) and \
            notes[i].duration.quarterLength == 0.5 and notes[i+1].duration.quarterLength == 0.25 and notes[i+2].duration.quarterLength == 0.25:
            # 8分音符，16分音符，16分音符の組み合わせをチェック
            if down_up[i] == 1:
                new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
                i += 3
            else:
                new_notes.append(notes[i])
                i += 1
        elif i + 2 < len(notes) and all(isinstance(n, note.Note) for n in notes[i:i+3]) and \
            notes[i].duration.quarterLength == 0.25 and notes[i+1].duration.quarterLength == 0.25 and notes[i+2].duration.quarterLength == 0.5:
            # 16分音符，16分音符，8分音符の組み合わせをチェック
            if down_up[i] == 1:
                new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
                i += 3
            else:
                new_notes.append(notes[i])
                i += 1

        else:
            # 音符をそのまま新しいリストに追加
            new_notes.append(notes[i])
            i += 1
        
    return new_notes


# 16分音符2連続なら変換
def update_note_eighth(notes, new_noteAndRest,down_up):
    """
    音符のリストを受け取り、16分音符と8分音符の連続を四分音符に変換した新しい音符のリストを返す関数
    """
    new_notes = []
    i = 0

    while i < len(notes):


        if isinstance(notes[i], note.Rest):
            # 元の音符が休符の場合、そのまま新しいリストに追加
            new_notes.append(notes[i])
            i += 1
            if i + 2 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.25 for n in notes[i:i+3]):
                if all(n == -1 for n in down_up[i:i+3]):
                    new_notes.append(create_augmentOrDiminish(notes[i],new_noteAndRest[i]))
                    i += 3
        elif i + 1 < len(notes) and all(n.duration.quarterLength == 0.25 for n in notes[i:i+2]):
            # 16分音符が2つ連続しているかチェック
            if down_up[i] == 1 and isinstance(notes[i],note.Note):
                new_notes.append(create_new_note_eighth(notes[i], new_noteAndRest[i]))
                i += 2
            else:
                new_notes.append(notes[i])
                i += 1

        else:
            # 音符をそのまま新しいリストに追加
            new_notes.append(notes[i])
            i += 1
        
    return new_notes


# def update_note_quarter(notes, new_noteAndRest,down_up):
#     """
#     音符のリストを受け取り、16分音符と8分音符の連続を四分音符に変換した新しい音符のリストを返す関数
#     """
#     new_notes = []
#     i = 0

#     while i < len(notes):
#         if isinstance(notes[i], note.Rest):
#             # 元の音符が休符の場合、そのまま新しいリストに追加
#             new_notes.append(notes[i])
#             i += 1

#         elif i + 3 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.25 for n in notes[i:i+4]):
#             # 16分音符が4つ連続しているかチェック
#             if down_up[i] == 1:
#                 new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
#                 i += 4
#             else:
#                 new_notes.append(notes[i])
#                 i += 1

#         elif i + 2 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.25 for n in notes[i:i+3]):
#                 if all(n == -1 for n in down_up[i:i+3]):
#                     new_notes.append(create_augmentOrDiminish(notes[i],new_noteAndRest[i]))
#                     i += 3
#         elif i + 1 < len(notes) and all(isinstance(n, note.Note) and n.duration.quarterLength == 0.5 for n in notes[i:i+2]):
#             # 8分音符が2つ連続しているかチェック
#             if down_up[i] == 1:
#                 new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
#                 i += 2
#             else:
#                 new_notes.append(notes[i])
#                 i += 1
#         elif i + 2 < len(notes) and all(isinstance(n, note.Note) for n in notes[i:i+3]) and \
#             notes[i].duration.quarterLength == 0.5 and notes[i+1].duration.quarterLength == 0.25 and notes[i+2].duration.quarterLength == 0.25:
#             # 8分音符，16分音符，16分音符の組み合わせをチェック
#             if down_up[i] == 1:
#                 new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
#                 i += 3
#             else:
#                 new_notes.append(notes[i])
#                 i += 1
#         elif i + 2 < len(notes) and all(isinstance(n, note.Note) for n in notes[i:i+3]) and \
#             notes[i].duration.quarterLength == 0.25 and notes[i+1].duration.quarterLength == 0.25 and notes[i+2].duration.quarterLength == 0.5:
#             # 16分音符，16分音符，8分音符の組み合わせをチェック
#             if down_up[i] == 1:
#                 new_notes.append(create_new_note(notes[i], new_noteAndRest[i]))
#                 i += 3
#             else:
#                 new_notes.append(notes[i])
#                 i += 1

#         else:
#             # 音符をそのまま新しいリストに追加
#             new_notes.append(notes[i])
#             i += 1
        
#     return new_notes
