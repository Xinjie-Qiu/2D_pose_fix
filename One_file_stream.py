import os
import cv2

#影片資料夾
video_source_folder = '.\\video'
#輸出資料夾
output_path = '.\\fix_skeleton'
if not os.path.exists(output_path):
    os.mkdir(output_path)
fix_filenames = os.listdir(output_path)
#2D_pose資料夾
data_path = '.\\skeleton'
filenames = os.listdir(data_path)
for fix in fix_filenames:
    filenames.remove(fix)
joint_name_list = ['鼻子','頸','右肩','右手腕','右肘','左肩','左手腕','左肘','右髖','右膝','右踝','左髖','左膝','左踝','右眼','左眼','右耳','左耳',
                   '2鼻子', '2頸', '2右肩', '2右手腕', '2右肘', '2左肩', '2左手腕', '2左肘', '2右髖', '2右膝', '2右踝', '2左髖', '2左膝', '2左踝',
                   '2右眼', '2左眼', '2右耳', '2左耳',]
joint_name_list_eng = ['Nose','Neck','RShoulder','RElbow','RWrist','LShoulder','LElbow','LWrist','RHip','RKnee','RAnkle','LHip','LKnee','LAnkle','REye','LEye','REar','LEar',
                       'rNose','2Neck','2RShoulder','2RElbow','2RWrist','2LShoulder','2LElbow','2LWrist','2RHip','2RKnee','2RAnkle','2LHip','2LKnee','2LAnkle','2REye','2LEye','2REar','2LEar']
XY_save_list = []

def _one_file_stream(filename):
    '''
    得到skeleton.txt內的每行資訊
    :param filename:
    :return:
    '''
    filename_path = os.path.join(data_path,filename)
    lines = open(filename_path,'r')
    lines = list(lines)
    return lines

def _get_missing_point(lines,filename):
    '''
    得到skeleton.txt內的遺失的骨架
    偵測0.0
    回傳[frame_num,joints_num]
    :param lines:
    :param filename:
    :return:
    '''

    miss_list = []
    line_num = len(lines)
    frames_num = int(lines[0].split('\n')[0])
    people_num = int(lines[1].split('\n')[0])

    action = int(filename[-11:-8])
    if action in range(50,61):
        real_people_num = 2
    else:
        real_people_num = 1

    if (real_people_num==1):
        tmp_line_num = 2
        for i in range(0,frames_num):
            for indx in range(0,19):
                tmp_list = []
                if ((float(lines[tmp_line_num].split('\n')[0].split()[0]) == 0.0) & (indx not in [1, 15, 16, 17, 18])):
                    tmp_list.append(i)
                    tmp_list.append(indx)
                    miss_list.append(tmp_list)
                tmp_line_num+=1
    elif (real_people_num==2):
        tmp_line_num = 2
        for i in range(0, frames_num):
            for indx in range(0, 38):
                tmp_list = []
                if ((float(lines[tmp_line_num].split('\n')[0].split()[0]) == 0.0)& (indx not in [1, 15, 16, 17, 18,20,34,35,36,37])):
                    tmp_list.append(i)
                    tmp_list.append(indx)
                    miss_list.append(tmp_list)
                tmp_line_num += 1
    return  miss_list

drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle. Press 'm' to toggle to curve
ix,iy = -1,-1

# mouse callback function
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing,mode
    global XY_save_list

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
        print(x,y)
        tmp = []
        tmp.append(x)
        tmp.append(y)
        XY_save_list.append(tmp)
        cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)


for filename in filenames:
    lines = _one_file_stream(filename)
    try:
        ms_point = _get_missing_point(lines,filename)
    except IndexError:
        with open('warning_log.txt', 'a') as f:
            f.write('{} out of range\n '.format(filename))
        filename_path = os.path.join(data_path, filename)
        os.remove(filename_path)
    video_name = filename[:-4]+'.avi'
    action = int(filename[-11:-8])
    if action in [50,51,52,53,54,55,56,57,58,59,60]:
        people_num = 2
    else:
        people_num = 1
    tmp_video_path = os.path.join(video_source_folder,video_name)

    tmp_num = 0
    ms_point_fix = ms_point
    for tmp_ms_point in ms_point_fix:
        if (len(ms_point_fix) < 30 and people_num == 1):
            # if it has pervious point and just copy it
            if (tmp_ms_point[0] == 0):
                frame_id = int(tmp_ms_point[0]) * 2
                joint_num = int(tmp_ms_point[1]) - 1
                cap = cv2.VideoCapture(tmp_video_path)
                cap.set(6, 30)
                cap.set(1, frame_id)
                ret, frame = cap.read()
                frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_LINEAR)
                if (people_num == 1):
                    for i in range(0, 18):
                        joint1_x = int(float(lines[2 + 19 * int(tmp_ms_point[0]) + i + 1].split('\n')[0].split()[0]))
                        joint1_y = int(float(lines[2 + 19 * int(tmp_ms_point[0]) + i + 1].split('\n')[0].split()[1]))
                        cv2.circle(frame, (joint1_x, joint1_y), 2, (0, 255, 0), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                img = cv2.putText(frame, 'Filename:' + str(filename), (30, 30), font, 1, (255, 0, 0), 3)
                img = cv2.putText(img, 'Frame_id:' + str(int(frame_id / 2)), (100, 100), font, 2, (255, 0, 0), 3)
                img = cv2.putText(img, joint_name_list_eng[joint_num], (200, 200), font, 3, (255, 0, 0),
                                  3)  # 添加文字，1.2表示字体大小，（0,40）是初始的位置，(255,255,255)表示颜色，2表示粗细
                print(joint_name_list[joint_num])
                cv2.namedWindow('image')
                cv2.setMouseCallback('image', draw_circle)
                while (1):
                    cv2.imshow('image', frame)
                    k = cv2.waitKey(1) & 0xFF
                    if k == ord('m'):
                        mode = not mode
                    elif k == 27:
                        break
                line_num = 3 + frame_id * 19 + joint_num
                tmp_string = '{} {} 0.000000\n'.format(XY_save_list[0][0], XY_save_list[0][1])
                lines[line_num] = tmp_string
                cap.release()
                cv2.destroyAllWindows()
            if (tmp_ms_point[0] > 0 and lines[19 * (tmp_ms_point[0] - 1) + tmp_ms_point[1] + 2] != '0.000000 0.000000 0.000000\n'):
                lines[19 * (tmp_ms_point[0]) + tmp_ms_point[1] + 2] = lines[19 * (tmp_ms_point[0] - 1) + tmp_ms_point[1] + 2]

    ms_point = _get_missing_point(lines, filename)
    for tmp_ms_point in ms_point:
        if(len(ms_point) < 30 and people_num == 1):
            frame_id = int(tmp_ms_point[0])*2
            joint_num = int(tmp_ms_point[1])-1
            cap = cv2.VideoCapture(tmp_video_path)
            cap.set(6, 30)
            cap.set(1, frame_id)
            ret, frame = cap.read()
            frame = cv2.resize(frame,(960,540),interpolation=cv2.INTER_LINEAR)
            if (people_num==1):
                for i in range(0,18):
                    joint1_x=int(float(lines[2+19*int(tmp_ms_point[0])+i+1].split('\n')[0].split()[0]))
                    joint1_y = int(float(lines[2 + 19 * int(tmp_ms_point[0]) + i+1].split('\n')[0].split()[1]))
                    cv2.circle(frame, (joint1_x, joint1_y), 2, (0, 255, 0), -1)
            else:
                for i in range(0,18):
                    joint1_x=int(float(lines[2+38*int(tmp_ms_point[0])+i+1].split('\n')[0].split()[0]))
                    joint1_y = int(float(lines[2 + 38 * int(tmp_ms_point[0]) + i+1].split('\n')[0].split()[1]))
                    cv2.circle(frame, (joint1_x, joint1_y), 2, (0, 255, 0), -1)
                for i in range(0,18):
                    joint1_x=int(float(lines[2+38*int(tmp_ms_point[0])+i+1+19].split('\n')[0].split()[0]))
                    joint1_y = int(float(lines[2 + 38 * int(tmp_ms_point[0]) + i+1+19].split('\n')[0].split()[1]))
                    cv2.circle(frame, (joint1_x, joint1_y), 2, (0, 255, 0), -1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            img = cv2.putText(frame, 'Filename:'+str(filename), (30, 30), font, 1, (255, 0, 0),3)
            img = cv2.putText(img, 'Frame_id:'+str(int(frame_id/2)), (100, 100), font, 2, (255, 0, 0),3)
            img = cv2.putText(img, joint_name_list_eng[joint_num], (200, 200), font, 3, (255, 0, 0),
                              3)  # 添加文字，1.2表示字体大小，（0,40）是初始的位置，(255,255,255)表示颜色，2表示粗细
            print(joint_name_list[joint_num])
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', draw_circle)
            while (1):
                cv2.imshow('image', frame)
                k = cv2.waitKey(1) & 0xFF
                if k == ord('m'):
                    mode = not mode
                elif k == 27:
                    break
            tmp_num+=1
    if (len(ms_point) != 0 and len(ms_point) < 30 and people_num == 1):
        cap.release()
        cv2.destroyAllWindows()
    if (len(ms_point_fix)!=0 and len(ms_point)<30 and people_num == 1):
        if (people_num==1):

            for i in range(0,len(ms_point)):
                frame_id = int(ms_point[i][0])
                joint_num = int(ms_point[i][1])-1
                line_num = 3+frame_id*19+joint_num
                tmp_string = '{} {} 0.000000\n'.format(XY_save_list[i][0],XY_save_list[i][1])
                lines[line_num] = tmp_string

            tmp_output_txt = os.path.join(output_path,filename)
            tmp_output_txt_writer =open(tmp_output_txt,'a')
            for line in lines:
                tmp_output_txt_writer.write(line)
                tmp_output_txt_writer.flush()
            tmp_output_txt_writer.close()
        else:
            for i in range(0, len(ms_point)):
                frame_id = int(ms_point[i][0])
                joint_num = int(ms_point[i][1]) - 1
                line_num = 3 + frame_id * 38 + joint_num
                tmp_string = '{} {} 0.000000\n'.format(XY_save_list[i][0], XY_save_list[i][1])
                lines[line_num] = tmp_string

            tmp_output_txt = os.path.join(output_path, filename)
            tmp_output_txt_writer = open(tmp_output_txt, 'a')
            for line in lines:
                tmp_output_txt_writer.write(line)
                tmp_output_txt_writer.flush()
            tmp_output_txt_writer.close()
        print(XY_save_list)
        XY_save_list = []

