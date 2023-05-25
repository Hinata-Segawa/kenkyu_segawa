
    for i in range(len(b)):
        if notes[i].isNote:
            notes[i].articulations = [articulations.StringIndication(b[i]%6+1)
                                    ,articulations.FretIndication(b[i]//6)]
            
            #新しい押弦位置のpitchに更新
            p = frets_items[b[i]][0]
            notes[i].pitch = pitch.Pitch(p)

