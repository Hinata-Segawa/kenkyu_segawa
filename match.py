from music21 import *
import csv
import os
import glob

def load_notes_from_file(file_path):
    """指定されたファイルからノートと休符を読み込む"""
    parsed_data = converter.parse(file_path)
    return [element for element in parsed_data.flat.notes]


def count_matching_pitches(input_notes, output_notes):
    """二つのノートリスト間でピッチが異名同音であるノートの数をカウントする"""
    return sum(1 for i, note in enumerate(input_notes) if note.pitch.ps == output_notes[i].pitch.ps)


def append_to_csv(input_file_name, total_notes, matches, file_path):
    """結果をCSVファイルに追記する"""
    match_rate = matches / total_notes if total_notes > 0 else 0
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow([input_file_name, total_notes, matches, match_rate])

# 結果を保存するCSVファイル名
results_csv = 'all_results_ビタビ.csv'

# CSVヘッダーの書き込み
with open(results_csv, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(["Input File", "Total Notes", "Matches", "Match Rate"])

# XML/ディレクトリ内の全ての.musicxmlファイルを取得
input_files = glob.glob("XML/*.musicxml")

for input_file in input_files:
    # 対応する出力ファイル名を生成
    base_name = os.path.basename(input_file)
    output_file = "out/" + os.path.splitext(base_name)[0] + "_output1_0.5.musicxml"

    # ファイルが存在するか確認
    if not os.path.exists(output_file):
        print(f"対応する出力ファイルが見つかりません: {output_file}")
        continue

    # ファイルの読み込み
    input_notes = load_notes_from_file(input_file)
    output_notes = load_notes_from_file(output_file)

    # ピッチが一致するノートの数をカウント
    matches = count_matching_pitches(input_notes, output_notes)

    # 結果をCSVファイルに追記
    append_to_csv(base_name, len(input_notes), matches, results_csv)

print(f"全ての結果がCSVファイルに書き出されました: {results_csv}")



