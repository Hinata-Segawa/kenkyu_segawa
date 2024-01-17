from music21 import *
from xmlRead import *
from HMM import *
from update import *
from measure import *
import os
import glob




class MusicScore:
    def __init__(self, xml_file,beat):
        self.xml_file = xml_file
        self.input = converter.parse(xml_file)
        self.notes = []
        self.note_only = []
        self.sf = []
        self.down_up1 = []#音符のみの表拍か裏拍か
        self.down_up2 = []#音符と休符両方ある表拍か裏拍か
        self.frets_items = None  
        self.n_states = None
        self.beat = beat
        self.key = None

    #notesに情報をいれたり，表拍か裏拍かを判定する
    def analyze_notes(self):
        for element in self.input.flat.notesAndRests:
            self.notes.append(element)
            if element.isNote:
                self.note_only.append(element)
                self.sf.append(element.articulations[0].number +
                               6 * element.articulations[1].number - 1)
                # print("sf:",element.articulations[0].number,element.articulations[1].number)
        self.down_up1 = judge_downup(self.note_only,self.beat)
        self.down_up2 = judge_downup(self.notes,self.beat)
   

        # 小節情報を探す
        num = 0
        for i in range(len(self.input)):
            if type(self.input[i]) == stream.Part:
                num = i
                break
        # 取得した楽譜の小節数
        self.length = len(self.input[num])

        self.key = get_first_key_signature_from_score(self.input)
        print(self.key)

    #ビタビアルゴリズムを適用
    def analyze_hmm(self):
        states, frets = guitar_frets_dict()
        self.n_states = len(states)
        self.frets_items = get_items(frets)
        observations = [i for i in self.sf]
        res = HMM_guitar(observations, self.down_up1,self.key)
        self.res = res
        

    #結果からnew_note_and_restに情報を入れる
    def update_notes(self):
        new_note_and_rest = []
        init_new_noteAndRest(new_note_and_rest, self.notes, self.res)
        update_note(self.notes, new_note_and_rest, self.frets_items)
        self.new_note_and_rest = new_note_and_rest
        

    #結果からquarter_notesに，四分音符にまとめた情報を入れる
    def update_quarter_notes(self):
        quarter_notes = []
        quarter_notes = update_note_quarter(self.notes, self.new_note_and_rest, self.down_up2)
        self.quarter_notes = quarter_notes

    #結果からeighth_notesに，八分音符にまとめた情報を入れる
    def update_eighth_notes(self):
        eighth_notes = []
        eighth_notes = update_note_eighth(self.notes, self.new_note_and_rest, self.down_up2)
        self.eighth_notes = eighth_notes

    #TAB譜作成
    def create_score(self, st):
        score = stream.Score()
        score.insert(0, metadata.Metadata())
        score.metadata.title = self.input.flat.metadata.title + "(HMMあり)"
        score.metadata.composer = self.input.flat.metadata.composer
        score.metadata.lyricist = self.input.flat.metadata.lyricist
        score.append(layout.ScoreLayout())
        score.append(st)
        return score

    #作ったTABにチューニング情報を入れる
    def generate_score(self, notes, output_file):
        st = stream.Stream()
        make_Measures(self.input, st, notes, self.length,self.key)
        score = self.create_score(st)
        score.write("musicxml", fp=output_file)
        modify_musicxml(output_file)



#結果をそのまま出力
class MusicScore1(MusicScore):
    def __init__(self, base_score):
        self.__dict__ = base_score.__dict__.copy()

    def generate(self):
        self.generate_score(self.notes, "output1.musicxml")

#四分音符にまとめて出力
class MusicScore2(MusicScore):
    def __init__(self, base_score):
        self.__dict__ = base_score.__dict__.copy()

    def generate(self):
        self.generate_score(self.quarter_notes, "output2.musicxml")

#八分音符にまとめて出力
class MusicScore3(MusicScore):
    def __init__(self, base_score):
        self.__dict__ = base_score.__dict__.copy()

    def generate(self):
        self.generate_score(self.eighth_notes, "output3.musicxml")




def get_musicxml_files(directory):
    return glob.glob(os.path.join(directory, "*.musicxml"))




def get_musicxml_filenames(directory="XML"):
    # XMLディレクトリ内のmusicxmlファイルのパスを取得
    filepaths = glob.glob(os.path.join(directory, "*.musicxml"))
    
    # ファイルパスからファイル名（拡張子を除いたもの）を取得
    filenames = [os.path.splitext(os.path.basename(filepath))[0] for filepath in filepaths]
    
    return filenames




# 最初のキーシグネチャを取得する関数
def get_first_key_signature_from_score(s):
    for part in s.parts:
        for measure in part.getElementsByClass('Measure'):
            ks = measure.getElementsByClass('KeySignature')
            if ks:
                return ks[0].asKey()
    return None


if __name__ == "__main__":
    file = "XML/Motor_Man.musicxml"
    base_score = MusicScore(file, 0.5) #1.0だと四分音符レベル，0.5だと八分音符レベル
    base_score.analyze_notes()
    base_score.analyze_hmm()


    score1 = MusicScore1(base_score)
    score1.update_notes()
    output_name1 = os.path.join("out", os.path.splitext(os.path.basename(file))[0] + "_output1_0.5.musicxml")
    score1.generate_score(score1.notes, output_name1)


    # for xml_file in get_musicxml_files("XML"):
        # base_score = MusicScore(xml_file, 1.0)
        # base_score.analyze_notes()
        # base_score.analyze_hmm()

        # score1 = MusicScore1(base_score)
        # score1.update_notes()
        # output_name1 = os.path.join("out", os.path.splitext(os.path.basename(xml_file))[0] + "_output1.musicxml")
        # score1.generate_score(score1.notes, output_name1)

        # score2 = MusicScore2(base_score)
        # score2.update_notes()
        # score2.update_quarter_notes()
        # output_name2 = os.path.join("out", os.path.splitext(os.path.basename(xml_file))[0] + "_output2_1.0.musicxml")
        # score2.generate_score(score2.quarter_notes, output_name2)

