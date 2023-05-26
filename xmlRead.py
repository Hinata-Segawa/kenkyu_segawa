import xml.etree.ElementTree as ET

def get_part_id(xml_file):
    # XMLデータの解析
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # idの取得
    target_id = None
    for p_elem in root.findall('part'):
        target_id = p_elem
    p_id = target_id.get('id')

    return p_id

def remove_unnecessary_element(root, p_id):
    # いらない部分を消す
    parent_element = root.find("part[@id='"+p_id+"']/measure[@number='1']/attributes")
    target_element = parent_element.find("staff-details[@print-object='yes']")
    parent_element.remove(target_element)

def add_staff_details(root, p_id):
    # 弦を6にする
    parent_element = root.find("part[@id='"+p_id+"']/measure[@number='1']/attributes")
    s_name = ET.SubElement(parent_element, 'staff-details')
    line_name = ET.SubElement(s_name, 'staff-lines')
    line_name.text = "6"

def add_tuning_info(root, p_id, step, octave):
    # チューニング情報の追加
    parent_element = root.find("part[@id='"+p_id+"']/measure[@number='1']/attributes/staff-details")
    
    for i in range(len(step)):
        # 1~6弦までの情報を追加
        tuning_name = ET.SubElement(parent_element, 'staff-tuning')
        tuning_name.set('line', str(i + 1))
        step_name = ET.SubElement(tuning_name, 'tuning-step')
        step_name.text = step[i]
        octave_name = ET.SubElement(tuning_name, 'tuning-octave')
        octave_name.text = octave[i]

def add_staff_size(root, p_id, scaling, size):
    # staff-sizeの追加
    parent_element = root.find("part[@id='"+p_id+"']/measure[@number='1']/attributes")
    s_size = ET.SubElement(parent_element, "staff-size")
    s_size.set("scaling", str(scaling))
    s_size.text = str(size)

def modify_musicxml(xml_file):
    # XMLデータの解析
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # idの取得
    p_id = get_part_id(xml_file)

    # いらない部分を消す
    remove_unnecessary_element(root, p_id)

    # 弦を6にする
    add_staff_details(root, p_id)

    # 音の種類とオクターブ
    step = ["E", "A", "D", "G", "B", "E"]
    octave = ["2", "2", "3", "3", "3", "4"]

    # チューニング情報の追加
    add_tuning_info(root, p_id, step, octave)

    # staff-sizeの追加
    add_staff_size(root, p_id, 100, 167)

    # 結果の保存
    # modified_file = xml_file.split('.')[0] + "_modified.musicxml"
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    return xml_file

#
