from music21 import *
# musicXMLファイルをロード
score = converter.parse("XML/dear_my_friend.musicxml")

# 最初のキーシグネチャを取得する関数
def get_first_key_signature_from_score(s):
    for part in s.parts:
        for measure in part.getElementsByClass('Measure'):
            ks = measure.getElementsByClass('KeySignature')
            if ks:
                return ks[0].asKey()
    return None


def is_note_in_scale(n, key):
    """指定された音符がキーシグネチャのスケールに含まれているかを判定する関数"""

    if not key:
        print("No key signature provided.")
        return False

    # スケールの音符を取得
    scale_notes = [p.name for p in scale.MajorScale(key.tonic).pitches[:-1]]

    # 音符がスケールに含まれているかを判定
    return note.Note(n).name in scale_notes


# 曲のキーシグネチャを取得
keys = get_first_key_signature_from_score(score)
print(keys)



n = ["A4","B5","B6"]

result = is_note_in_scale(n[1], keys)
print(f"{n[1]} is in the scale: {result}")