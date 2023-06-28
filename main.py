from music21 import *
import itertools
import numpy as np
from xmlRead import *
from HMM import *


def guitar_frets_dict():
    # 開放弦から20フレット分
    frets = [
        {"E4": 0, "F4": 6,  "F#4": 12, "G4": 18, "G#4": 24, "A4": 30, "A#4": 36, "B4": 42, "C5": 48, "C#5": 54, "D5": 60,
            "D#5": 66, "E5": 72, "F5": 78, "F#5": 84, "G5": 90, "G#5": 96, "A5": 102, "A#5": 108, "B5": 114, "C6": 120},
        {"B3": 1, "C3": 7,  "C#4": 13, "D4": 19, "D#4": 25, "E4": 31, "F4": 37, "F#4": 43, "G4": 49, "G#4": 55, "A4": 61,
            "A#4": 67, "B4": 73, "C5": 79, "C#5": 85, "D5": 91, "D#5": 97, "E5": 103, "F5": 109, "F#5": 115, "G5": 121},
        {"G3": 2, "G#3": 8,  "A3": 14, "A#3": 20, "B3": 26, "C4": 32, "C#4": 38, "D4": 44, "D#4": 50, "E4":  56, "F4": 62,
            "F#4": 68, "G4": 74, "G#4": 80, "A4": 86, "A#4": 92, "B4": 98, "C5": 104, "C#5": 110, "D5": 116, "D#5": 122},
        {"D3": 3, "D#3": 9,  "E3": 15, "F3": 21, "F#3": 27, "G3": 33, "G#3": 39, "A3": 45, "A#3": 51, "B3":  57, "C4": 63,
            "C#4": 69, "D4": 75, "D#4": 81, "E4": 87, "F4": 93, "F#4": 99, "G4": 105, "G#4": 111, "A4": 117, "A#4": 123},
        {"A2": 4, "A#2": 10, "B2": 16, "C3": 22, "C#3": 28, "D3": 34, "D#3": 40, "E3": 46, "F3": 52, "F#3": 58, "G3": 64,
            "G#3": 70, "A3": 76, "A#3": 82, "B3": 88, "C4": 94, "C#4": 100, "D4": 106, "D#4": 112, "E4": 118, "F4": 124},
        {"E2": 5, "F2": 11, "F#2": 17, "G2": 23, "G#2": 29, "A2": 35, "A#2": 41, "B2": 47, "C3": 53, "C#3": 59, "D3": 65,
            "D#3": 71, "E3": 77, "F3": 83, "F#3": 89, "G3": 95, "G#3": 101, "A3": 107, "A#3": 113, "B3": 119, "C4": 125}
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


#四分音符レベルで裏拍を判断する
def judge_downup(notes):
    down_up = []
    count = 1

    for note in notes:
        offset = note.offset

        # 10かけて10で割った余りが0なら表拍
        if (offset * 10) % 10 == 0:
            # 表拍
            down_up.append(1)
            # print(count,":表")
        else:
            # 裏拍
            down_up.append(-1)
            # print(count,":裏")

        count += 1
    return down_up


def Init(m, Input):
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
    keys = key.KeySignature(Input.analyze("key").sharps)
    # k = key.Key("d")
    m.append(keys)
    t_Signature = meter.TimeSignature()
    m.append(t_Signature)

    return m


def make_Measures(Input, St, notes, length):
    index = 0
    for i in range(1, length):
        m = stream.Measure(number=i)
        # 1小節目(初期情報入力)
        if i == 1:
            m = Init(m, Input)
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


def update_note(notes, new_noteAndRest):
    for i in range(len(notes)):
        if notes[i].isNote:
            notes[i].articulations = [articulations.StringIndication(
                new_noteAndRest[i] % 6+1), articulations.FretIndication(new_noteAndRest[i]//6)]

            # 新しい押弦位置のpitchに更新
            p = frets_items[new_noteAndRest[i]][0]
            notes[i].pitch = pitch.Pitch(p)


def init_new_noteAndRest(new_noteAndRest):
    count = 0
    # 休符は-1にして新しく配列に入れる
    for i in range(len(notes)):
        if notes[i].isNote:
            new_noteAndRest.append(res[count])
            count += 1
        else:
            new_noteAndRest.append(-1)


if __name__ == "__main__":
    Input = converter.parse("XML\\ツキカゲ.musicxml")

    # 音符と休符
    notes = []

    # 音符だけ
    note_only = []

    sf = []
    down_up = []

    # 音符と休符の情報を入れる
    for i in range(len(Input.flat.notesAndRests)):
        notes.append(Input.flat.notesAndRests[i])

    # sfにs+6fの値を入れる
    for i in range(len(notes)):
        if notes[i].isNote:
            sf.append(notes[i].articulations[0].number +
                      6*notes[i].articulations[1].number-1)
            note_only.append(notes[i])

    # 表拍か裏拍かを判断してdown_upに入れる
    down_up = judge_downup(note_only)

    # 小節情報を探す
    num = 0
    for i in range(len(Input)):
        if type(Input[i]) == stream.Part:
            num = i
            break

    states, frets = guitar_frets_dict()
    n_states = len(states)  # 長さ(126)
    frets_items = get_items(frets)  # 音の番号と種類

    observations = [i for i in sf]

    # print("ob=",observations)

    # for i in range(len(observations)):
    # #   print(observations[i]%6+1,"弦",observations[i]//6,"フレット",frets_items[sf[i]][0])

    # ビタビに入れた結果をresに代入
    res = HMM_guitar(observations, down_up)

    print(res)
    print("出力=")
    for i in range(len(res)):
        print(res[i]%6+1,"弦",res[i]//6,"フレット",frets_items[res[i]][0])

    new_noteAndRest = []

    # 新しい音符と休符を入れる
    init_new_noteAndRest(new_noteAndRest)

    # 押弦位置の変わった場所のnoteを変える
    update_note(notes, new_noteAndRest)



    # 取得した楽譜の小節数
    length = len(Input[num])
    print("Input[num]=", Input[num])

    print("小節:", length)

    # 楽譜の基盤
    score = stream.Score()

    # ここで楽器情報をギターにする
    inst = instrument.ElectricGuitar()
    stream1 = stream.Stream()


    # 小節
    make_Measures(Input, stream1, notes, length)
    score.append(stream1)
    score.insert(0, metadata.Metadata())

    score.metadata.title = Input.flat.metadata.title + "(HMMあり)"
    score.metadata.composer = Input.flat.metadata.composer
    score.metadata.lyricist = Input.flat.metadata.lyricist
    score.append(layout.ScoreLayout())

    score.write("musicxml", fp="output.musicxml")

    score.show()

    # チューニング情報入れる
    # modify_musicxml("output.musicxml")

    # #たしかめ
    # op = converter.parse("output.musicxml")

    # a = []
    # for i in range(len(op.flat.notesAndRests)):
    #     a.append(op.flat.notesAndRests[i])

    # for i in range(len(a)):
    #     print(i+1,":",a[i].duration.quarterLength)

    # output = converter.parse("output.musicxml")
    # output.show()
