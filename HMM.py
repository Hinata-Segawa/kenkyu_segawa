import hmmlearn
from hmmlearn import hmm
import numpy as np
import random
import itertools
import math
import copy
# 観測値


def guitar_frets_dict():
    # 開放弦から20フレット分
    frets = [
        {"E5": 0, "F5": 6,  "F#5":12, "G5":18, "G#5":24, "A5":30, "A#5":36, "B5": 42, "C6": 48, "C#6": 54, "D6": 60, "D#6": 66,"E6": 72,"F6":78,"F#6":84,"G6":90,"G#6":96,"A6":102,"A#6":108,"B6":114,"C7":120},
        {"B4": 1, "C5": 7,  "C#5":13, "D5":19, "D#5":25, "E5":31, "F5": 37, "F#5":43, "G5": 49, "G#5": 55, "A5": 61, "A#5": 67,"B5": 73,"C6":79,"C#6":85,"D6":91,"D#6":97,"E6":103,"F6":109,"F#6":115,"G6":121},
        {"G4": 2, "G#4":8,  "A4": 14, "A#4":20,"B4": 26, "C5":32, "C#5":38, "D5": 44, "D#5":50, "E5":  56, "F5": 62, "F#5": 68,"G5": 74,"G#5":80,"A5":86, "A#5":92,"B5":98,"C6":104,"C#6":110,"D6":116,"D#6":122},
        {"D4": 3, "D#4":9,  "E4": 15, "F4":21, "F#4":27, "G4":33, "G#4":39, "A4": 45, "A#4":51, "B4":  57, "C5": 63, "C#5": 69,"D5": 75,"D#5":81,"E5":87, "F5":93,"F#5":99,"G5":105,"G#5":111,"A5":117,"A#5":123},
        {"A3": 4, "A#3":10, "B3": 16, "C4":22, "C#4":28, "D4":34, "D#4":40, "E4": 46, "F4": 52, "F#4": 58, "G4": 64, "G#4": 70,"A4": 76,"A#4":82,"B4":88, "C5":94,"C#5":100,"D5":106,"D#5":112,"E5":118,"F5":124},
        {"E3": 5, "F3": 11, "F#3":17, "G3":23, "G#3":29, "A3":35, "A#3":41, "B3": 47, "C4": 53, "C#4": 59, "D4": 65, "D#4": 71,"E4": 77,"F4":83,"F#4":89, "G4":95,"G#4":101,"A4":107,"A#4":113,"B4":119,"C5":125}
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


# 遷移確率
def init_transmat(n_observe_states, frets_items):

    trans = {}

    sum_list = [0]*n_observe_states  # 各行の数値の合計値のリスト

    for i in range(n_observe_states):
        append = {}
        for j in range(n_observe_states):

            # 4フレット離れていたら1を割り当て
            if cal_f_dist(i, j) < 4:
                append[j] = 1
                sum_list[i] += 1
                
                if j // 6 == 0:
                    append[j] = 50 

                # note = frets_items[i][0]  # 音の代入
                # 同じ音かつフレットの距離が2以下の時80を割り当て

                # if cal_f_dist(i, j) <= 2 and note == frets_items[j][0]:
                #     trans[i][j] = 80
                #     sum_list[i] += 30
            else:
                append[j] = 50

        trans[i] = append

    return trans


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



def viterbi(observs, states, sp, tp, ep,du):
    """viterbi algorithm
    Output : labels estimated"""
    T = {}  # present state
    for st in states:
        T[st] = (sp[st]+ep[st][observs[0]], [st])


    for i in range(len(observs)-1):
        ob = observs[i+1]
        T = next_state(ob, states, T, tp, ep,du[i+1])
    prob, labels = min([T[st] for st in T])


    return prob, labels


def next_state(ob, states, T, tp, ep,du):
    """calculate a next state's probability, and get a next path"""
    U = {}  # next state
    for next_s in states:
        U[next_s] = (1000, [])
        # print("next_s =",next_s)
        for now_s in states:
            # print("now_s =",now_s)
            p = T[now_s][0] + cal_cost(now_s,next_s,du) + ep[next_s][ob]
            if p < U[next_s][0]:
                U[next_s] = [p, T[now_s][1]+[next_s]]

    # print("U=", U)
    return U


def HMM_guitar(input,down_up):
    #(S,F)としたときにS+F = xとする． S = 弦，F = フレット ，0から125まで

    states, frets = guitar_frets_dict()
    n_states = len(states)  # 長さ(126)
    frets_items = get_items(frets)  # 音の番号と種類
    du = [[i for i in down_up]]



    observations = [[i for i in input]]
    # 例):[48, 50, 52, 53, 55, 55, 48, 50, 52, 53, 55, 55]


    # 初期コスト
    start_prob = init_startprob(n_states,observations)


    # 出力確率
    emmision_prob = init_emmisionprob(n_states, frets_items)
    
    # 遷移確率
    transit_prob = init_transmat(n_states,frets_items)


    a,b = viterbi(observations,states,start_prob,transit_prob,emmision_prob,down_up)


    print(b)
    print(a)


    # 出力
    res = []

    for i in range(len(b)):
      print(b[i]%6+1,"弦",b[i]//6,"フレット")
      res.append((b[i]%6 + 1, b[i]//6))

    return res


    