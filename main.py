from music21 import *
import itertools
import numpy as np
from xmlRead import *

def guitar_frets_dict():
    # 開放弦から20フレット分
    frets = [
        {"E4": 0, "F4": 6,  "F#4":12, "G4":18, "G#4":24, "A4":30, "A#4":36, "B4": 42, "C5": 48, "C#5": 54, "D5": 60, "D#5": 66,"E5": 72,"F5":78,"F#5":84,"G5":90,"G#5":96,"A5":102,"A#5":108,"B5":114,"C6":120},
        {"B3": 1, "C3": 7,  "C#4":13, "D4":19, "D#4":25, "E4":31, "F4": 37, "F#4":43, "G4": 49, "G#4": 55, "A4": 61, "A#4": 67,"B4": 73,"C5":79,"C#5":85,"D5":91,"D#5":97,"E5":103,"F5":109,"F#5":115,"G5":121},
        {"G3": 2, "G#3":8,  "A3": 14, "A#3":20,"B3": 26, "C4":32, "C#4":38, "D4": 44, "D#4":50, "E4":  56, "F4": 62, "F#4": 68,"G4": 74,"G#4":80,"A4":86, "A#4":92,"B4":98,"C5":104,"C#5":110,"D5":116,"D#5":122},
        {"D3": 3, "D#3":9,  "E3": 15, "F3":21, "F#3":27, "G3":33, "G#3":39, "A3": 45, "A#3":51, "B3":  57, "C4": 63, "C#4": 69,"D4": 75,"D#4":81,"E4":87, "F4":93,"F#4":99,"G4":105,"G#4":111,"A4":117,"A#4":123},
        {"A2": 4, "A#2":10, "B2": 16, "C3":22, "C#3":28, "D3":34, "D#3":40, "E3": 46, "F3": 52, "F#3": 58, "G3": 64, "G#3": 70,"A3": 76,"A#3":82,"B3":88, "C4":94,"C#4":100,"D4":106,"D#4":112,"E4":118,"F4":124},
        {"E2": 5, "F2": 11, "F#2":17, "G2":23, "G#2":29, "A2":35, "A#2":41, "B2": 47, "C3": 53, "C#3": 59, "D3": 65, "D#3": 71,"E3": 77,"F3":83,"F#3":89, "G3":95,"G#3":101,"A3":107,"A#3":113,"B3":119,"C4":125}
    ]
    note_number = [i for i in range(0, 126)]
    return note_number, frets



def get_items(frets):
  items = []

  #全部のキーと要素を抽出
  for i in range(6):
    items.append(list(frets[i].items()))

  # print(items)

  #二次元配列になっているので平坦化する
  items = list(itertools.chain.from_iterable(items))

  #番号順にソートする
  items = sorted(items, key = lambda x:x[1])

  return items


def cal_f_dist(a, b):
    dist = abs(a // 6 - b // 6)  # 次の音へのフレットの距離
    return dist




def cal_s_dist(a,b):
    dist = abs(a % 6 - b % 6)# 次の音への弦の距離
    return dist




def start_cal_cost(i):
    if i == -1:
        cost = 100000000
    else:
        cost = 1

    return cost



#コストの計算
def cal_cost(i,j,k):
    f_dist = cal_f_dist(i,j)
    s_dist = cal_s_dist(i,j)

    if k == -1:
        #押弦位置同じ
        if i == j:
            cost = 1
        else:
            cost = 100
        return cost

    #フレット移動距離4フレット未満
    if f_dist < 4:

        #開放弦禁止
        if j // 6 == 0:
            cost = 1000
        
        #フレット移動距離2フレット以上
        if s_dist >= 2:
            cost = 100
        else:
            cost = 1
    else:
        cost = 1000

    # print("cost =",cost)
    return cost



def normalization(data, sum_list):  # 正規化
  for i in range(len(data)):
    for j in range(len(data[0])):
      data[i][j] /= sum_list[i]

  return data


# def make_dist_list(data):
#   dist_list = []  # 次の音まで何フレット離れているかを格納するリスト

#   for i in range(len(data[0])-1):  # 最後の要素は次の音がないから走査する必要ない
#     dist = cal_dist(data[0][i], data[0][i+1])
#     dist_list.append(dist)

#   return dist_list



# 初期確率
def init_startprob(n_observe_states,observations):

    start_prob = {}

    for i in range(n_observe_states):
        #観測情報の先頭だけコストを軽くする
        if i == observations[0]:
            start_prob[i] = 1
        else:
            start_prob[i] = 100

    return start_prob




# 出力確率
def init_emmisionprob(n_observe_states, frets_items):
    emmision = {}


    # 100,80,1の割り当て
    for i in range(n_observe_states):
        append = {}
        i_key = frets_items[i][0]
        for j in range(n_observe_states):
            if i == j:  # 全部同じなら100
                append[j] = 1

            elif frets_items[j][0] == i_key:  # 同じ音なら10
                append[j] = 10

            else:
                append[j] = 50

        
        emmision[i] = append

    return emmision


def judge_downup(notes):
    down_up = []

    for note in notes:
        offset = note.offset

        if (offset *10) % 10 == 0:
            # 表拍
            down_up.append(1)
        else:
            # 裏拍
            down_up.append(-1)

    return down_up


def viterbi(observs, states, sp, ep,du):
    """viterbi algorithm
    Output : labels estimated"""
    T = {}  # present state
    for st in states:
        T[st] = (sp[st]+ep[st][observs[0]]+start_cal_cost(du[0]), [st])


    for i in range(len(observs)-1):
        ob = observs[i+1]
        T = next_state(ob, states, T,ep,du[i+1])
    prob, labels = min([T[st] for st in T])


    return prob, labels


def next_state(ob, states, T, ep,du):
    """calculate a next state's probability, and get a next path"""
    U = {}  # next state
    for next_s in states:
        U[next_s] = (1000000000, [])
        # print("next_s =",next_s)
        for now_s in states:
            # print("now_s =",now_s)
            p = T[now_s][0] + cal_cost(now_s,next_s,du) + ep[next_s][ob]
            if p < U[next_s][0]:
                U[next_s] = [p, T[now_s][1]+[next_s]]

    # print("U=", U)
    return U



def Init(m, Input):
    # 楽譜のレイアウトを決定
    Layout = layout.SystemLayout()
    m.append(Layout)
        
    # テンポ
    num = Input.metronomeMarkBoundaries()[0][2].number
    tmp = tempo.MetronomeMark(number = num)
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
        while d < 4.0 and index < len(notes):# 1小節内には4拍子分の音しか入らない
            sub_note = []# 音符格納用の配列
            d += notes[index].duration.quarterLength
            if notes[index].isChord:# コードなら
                sub_note.append(notes[index])

            elif notes[index].isNote:# 音符なら
                n = note.Note(notes[index].nameWithOctave, quarterLength = notes[index].duration.quarterLength)
                n.articulations = notes[index].articulations
                # print(n.nameWithOctave)
                if not notes[index].tie is None:# タイ記号があれば
                    n.tie = tie.Tie(notes[index].tie.type)
                sub_note.append(n)

            elif notes[index].isRest:# 休符なら
                sub_note.append(note.Rest(notes[index].duration.quarterLength))
            m.append(sub_note)
            index += 1

        if i == length-1:# 最後の小節に線を入れる
            line = bar.Barline(type="final")
            m.insert(0, line)
        St.append(m)



if __name__ == "__main__":
    Input = converter.parse("XML\\5.musicxml")   

    notes = []
    sf = []
    down_up = []




    for i in range(len(Input.flat.notesAndRests)):
        notes.append(Input.flat.notesAndRests[i])
    


    
    # print("lenFlat=",len(notes))




    for i in range(len(notes)):
        if notes[i].isNote:
            sf.append(notes[i].articulations[0].number + 6*notes[i].articulations[1].number-1)

    print("sf=",sf)
    # print("len=",len(sf))


    #表拍か裏拍か
    down_up = judge_downup(notes)



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
    print("ob=",observations)

    for i in range(len(observations)):
      print(observations[i]%6+1,"弦",observations[i]//6,"フレット",frets_items[sf[i]][0])
    


    # 初期コスト
    start_prob = init_startprob(n_states,observations)


    # 出力確率
    emmision_prob = init_emmisionprob(n_states, frets_items)
    

    a,b = viterbi(observations,states,start_prob,emmision_prob,down_up)

    # print("b=",b)
    # print("len=",len(b))
    # print(a)
    
    print("出力=")
    for i in range(len(b)):
        print(b[i]%6+1,"弦",b[i]//6,"フレット",frets_items[b[i]][0]) 


    new_noteAndRest = []
    count = 0

    #休符は-1にして新しく配列に入れる
    for i in range(len(notes)):
        if notes[i].isNote:
            new_noteAndRest.append(b[count])
            count += 1
        else:
            new_noteAndRest.append(-1)

    # print("len=",new_noteAndRest)

    for i in range(len(notes)):
        if notes[i].isNote:
            notes[i].articulations = [articulations.StringIndication(new_noteAndRest[i]%6+1)
                                    ,articulations.FretIndication(new_noteAndRest[i]//6)]
            
            #新しい押弦位置のpitchに更新
            p = frets_items[new_noteAndRest[i]][0]
            notes[i].pitch = pitch.Pitch(p)





    # 取得した楽譜の小節数        
    length = len(Input[num])



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

    #チューニング情報入れる
    modify_musicxml("output.musicxml")

    # output = converter.parse("output_modified.musicxml")
    # output.show()

    

    # score.show()
