# 最初のキーシグネチャを取得する関数
def get_first_key_signature_from_score(s):
    for part in s.parts:
        for measure in part.getElementsByClass('Measure'):
            ks = measure.getElementsByClass('KeySignature')
            if ks:
                return ks[0].asKey()
    return None

