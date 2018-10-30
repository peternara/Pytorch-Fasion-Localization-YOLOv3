import glob
import json
import os
import random
import shutil

def load_classes(path):
    """
    Loads class labels at 'path'
    """
    fp = open(path, "r")
    names = fp.read().split("\n")[:-1]
    fp.close()
    return names


W, H = 1280, 720

# key: img_name
# value: emotion, x, y, w, h
GT_imgs = dict()

classes = load_classes('bi_data/emotion.names')
print('classes:', classes)

A = ['images', 'labels']
B = ['train', 'val', 'test']
for a in A:
    os.makedirs('bi_data/' + a, exist_ok=True)
    for b in B:
        os.makedirs('bi_data/' + a + '/' + b, exist_ok=True)


for json_filename in glob.iglob('bi_data/*.json'):
    with open(json_filename, encoding='utf-8') as json_f:
        imgs = json.load(json_f, strict=False)["visual_results"]
        print(json_filename[8:17])
        # print(json_file, ':', len(js))
        
        for img_from_path in imgs:
            img_name = img_from_path["image"].replace('.jpg', '.txt').replace('.png', '.txt').split()[0]
            people = img_from_path["person"][0]
            out_str = ''
            for person in people.values():
                # coordinates
                coords = person[0]["full_rect"]
                try:
                    x1 = float(coords["min_x"])
                    y1 = float(coords["min_y"])
                    x2 = float(coords["max_x"])
                    y2 = float(coords["max_y"])
                except ValueError:
                    continue
                
                x = round((x1 + x2) / (2 * W), 6)
                y = round((y1 + y2) / (2 * H), 6)
                w = round((x2 - x1) / W, 6)
                h = round((y2 - y1) / H, 6)
                
                # emotion
                emotion = person[0]["emotion"].lower()
                class_num = classes.index(emotion)
                
                out_str += str(class_num) + ' ' + \
                           str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '\n'

            labels_filename = 'bi_data/labels/' + json_filename[8:17] + img_name

            if os.path.exists(labels_filename):
                labels_filename = labels_filename.replace('.txt', '_2.txt')

            if len(out_str) > 0:
                with open(labels_filename, 'w') as labels_file:
                    labels_file.write(out_str)


train_img_list_f = open('bi_data/train_img_list.txt', 'w')
val_img_list_f = open('bi_data/val_img_list.txt', 'w')

for img_path in glob.iglob('bi_data/**/*.jpg', recursive=True):
    img_from_path = img_path.replace('\\', '/')
    print('img_path:', img_from_path)
    season_episode = img_from_path.split('/')[1][:9]
    img_name = img_from_path.split('/')[-1].split()[0].replace('.png', 'jpg')
    
    label_from_path = 'bi_data/labels/'
    img_to_path = 'bi_data/images/'
    
    r = random.random()
    
    if r <= 0.89:
        mode = 'train/'
    elif r <= 0.99:
        mode = 'val/'
    else:
        mode = 'test/'
    
    img_to_path += mode
    img_to_path += season_episode + img_name

    if os.path.isfile(img_to_path):
        img_to_path = img_to_path.replace('.jpg', '_2.jpg')
    
    label_to_path = img_to_path.replace('images/', 'labels/').replace('.jpg', '.txt')
    label_from_path = label_to_path.replace(mode, '')

    if not os.path.exists(img_from_path) or not os.path.exists(label_from_path):
        continue
    
    os.rename(img_from_path, img_to_path)
    os.rename(label_from_path, label_to_path)
    # shutil.copy(img_from_path, img_to_path)
    # shutil.copy(label_from_path, label_to_path)

    if mode=='train/':
        train_img_list_f.write(img_to_path + '\n')
    elif mode=='val/':
        val_img_list_f.write(img_to_path + '\n')
    
    
train_img_list_f.close()
val_img_list_f.close()
