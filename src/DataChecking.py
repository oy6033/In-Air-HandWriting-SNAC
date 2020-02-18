import glob
import os




for i in range(0,100):
    lists = [x for x in range(i*100,(i+1)*100)]
    file_lists = []
    path_file_number=glob.glob('C:\Users\Michael\PycharmProjects\In-Air-HandWriting-SNAC\data_leap\Chinese//client2//'+str(i)+'//*')
    if len(path_file_number) != 100:
        print('group' + str(i))
        for root, dirs, files in os.walk(
                'C:\Users\Michael\PycharmProjects\In-Air-HandWriting-SNAC\data_leap\Chinese//client2//' + str(
                        i)):
            for file in files:
                file_lists.append(int(file.split('word')[1]))

            for list in lists:
                if list not in file_lists:
                    print 'lack of %d' % list
