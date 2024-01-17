from music21 import *
import itertools
import numpy as np
from xmlRead import *
from HMM import *
from update import *


def guitar_frets_dict():
    # 開放弦から20フレット分
    frets = [
        {"E4": 0, "F4": 6,  "F#4": 12, "G4": 18, "G#4": 24, "A4": 30, "A#4": 36, "B4": 42, "C5": 48, "C#5": 54, "D5": 60,"D#5": 66, "E5": 72, "F5": 78, "F#5": 84, "G5": 90, "G#5": 96, "A5": 102, "A#5": 108, "B5": 114, "C6": 120},
        {"B3": 1, "C3": 7,  "C#4": 13, "D4": 19, "D#4": 25, "E4": 31, "F4": 37, "F#4": 43, "G4": 49, "G#4": 55, "A4": 61,"A#4": 67, "B4": 73, "C5": 79, "C#5": 85, "D5": 91, "D#5": 97, "E5": 103, "F5": 109, "F#5": 115, "G5": 121},
        {"G3": 2, "G#3": 8,  "A3": 14, "A#3": 20, "B3": 26, "C4": 32, "C#4": 38, "D4": 44, "D#4": 50, "E4":  56, "F4": 62,"F#4": 68, "G4": 74, "G#4": 80, "A4": 86, "A#4": 92, "B4": 98, "C5": 104, "C#5": 110, "D5": 116, "D#5": 122},
        {"D3": 3, "D#3": 9,  "E3": 15, "F3": 21, "F#3": 27, "G3": 33, "G#3": 39, "A3": 45, "A#3": 51, "B3":  57, "C4": 63,"C#4": 69, "D4": 75, "D#4": 81, "E4": 87, "F4": 93, "F#4": 99, "G4": 105, "G#4": 111, "A4": 117, "A#4": 123},
        {"A2": 4, "A#2": 10, "B2": 16, "C3": 22, "C#3": 28, "D3": 34, "D#3": 40, "E3": 46, "F3": 52, "F#3": 58, "G3": 64,"G#3": 70, "A3": 76, "A#3": 82, "B3": 88, "C4": 94, "C#4": 100, "D4": 106, "D#4": 112, "E4": 118, "F4": 124},
        {"E2": 5, "F2": 11, "F#2": 17, "G2": 23, "G#2": 29, "A2": 35, "A#2": 41, "B2": 47, "C3": 53, "C#3": 59, "D3": 65,"D#3": 71, "E3": 77, "F3": 83, "F#3": 89, "G3": 95, "G#3": 101, "A3": 107, "A#3": 113, "B3": 119, "C4": 125}
    ]
    note_number = [i for i in range(0, 126)]
    return note_number, frets


def get_items(frets):
    items = []

    # 全部のキーと要素を抽出
    for i in range(6):
        items.append(list(frets[i].items()))

    # print(items)

    # 二次元配列になっているので平坦化する
    items = list(itertools.chain.from_iterable(items))

    # 番号順にソートする
    items = sorted(items, key=lambda x: x[1])

    return items



# 四分音符レベルで裏拍を判断する
def judge_downup(notes,beat):
    down_up = []
    count = 1

    for note in notes:
        offset = note.offset

        # 10かけて10で割った余りが0なら表拍
        print(offset)
        if (offset / beat) % 1 == 0:
            # 表拍
            down_up.append(1)
            # print(count,":表")
        else:
            # 裏拍
            down_up.append(-1)
            # print(count,":裏")
        count += 1
    return down_up


def Init(m, Input,key):
    # 楽譜のレイアウトを決定
    Layout = layout.SystemLayout()
    m.append(Layout)

    # テンポ
    num = Input.metronomeMarkBoundaries()[0][2].number
    tmp = tempo.MetronomeMark(number=num)
    m.append(tmp)

    # StaffLayoutで、五線譜やTABの六線譜を描画
    Staff_Layout = layout.StaffLayout(staffLines=6)
    m.append(Staff_Layout)

    # ここで表示する形式をTabにしている
    clf = clef.TabClef()
    clf.line = 6
    m.append(clf)

    # 調と拍子の情報(default: key = C, TimeSignature = 4/4)
    # keys = key.KeySignature(Input.analyze("key").sharps)
    # k = key.Key("d")
    m.append(key)
    t_Signature = meter.TimeSignature()
    m.append(t_Signature)

    return m


def make_Measures(Input, St, notes, length,key):
    index = 0
    for i in range(1, length):
        m = stream.Measure(number=i)
        # 1小節目(初期情報入力)
        if i == 1:
            m = Init(m, Input,key)
        if i % 4 == 1:
            # 4小節ごとに改行
            m.append(layout.SystemLayout(isNew=True))
        d = 0.0
        while d < 4.0 and index < len(notes):  # 1小節内には4拍子分の音しか入らない
            sub_note = []  # 音符格納用の配列
            d += notes[index].duration.quarterLength

            if notes[index].isNote:  # 音符なら
                n = note.Note(
                    notes[index].nameWithOctave, quarterLength=notes[index].duration.quarterLength)
                # print("note", index+1, ":",
                #       notes[index].duration.quarterLength)

                n.articulations = notes[index].articulations
                # print(n.nameWithOctave)
                if not notes[index].tie is None:  # タイ記号があれば
                    n.tie = tie.Tie(notes[index].tie.type)
                sub_note.append(n)

            elif notes[index].isRest:  # 休符なら
                rest = note.Rest()
                rest.duration.quarterLength = notes[index].duration.quarterLength

                sub_note.append(rest)

                # sub_note.append(note.Rest(notes[index].duration.quarterLength))
                # print("rest",index+1,":",notes[index].duration.quarterLength)
            # print(index+1, "sub:", sub_note)
            m.append(sub_note)

            index += 1

        if i == length-1:  # 最後の小節に線を入れる
            line = bar.Barline(type="final")
            m.insert(0, line)
        St.append(m)

