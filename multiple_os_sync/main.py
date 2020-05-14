import os
from pprint import pprint as pp

win_path='/masterstorage/steamlibrary_win_only/SteamLibrary/steamapps/common/'
lin_path='/motherstorage/SteamLibrary/steamapps/common/'
win_path2='/mnt/Program Files (x86)/Steam/steamapps/common/'
IGNORE_CONFLICTS_FILE='ignore_conflicts.txt'

def multiple_paths(paths):
    result = []
    for path in paths:
        for dir_name in os.listdir(path):
            result.append(dir_name)
    return result

def ignore_conflicts(conflicts, verbose=True):
    ignore_count = 0
    if os.path.exists(IGNORE_CONFLICTS_FILE):
        with open(IGNORE_CONFLICTS_FILE) as iow:
            ignore_list = []
            for dir_name in iow.readlines():
                if not dir_name.startswith('#') and len(dir_name) > 1:
                    ignore_list.append(dir_name.strip())
        for ignore_dir in ignore_list:
            conflicts.discard(ignore_dir)
            ignore_count+=1
            if verbose:
                print(f"Ignoring {ignore_dir}")
    else:
        print('No {} file, no ignoring')
    return conflicts, ignore_count


def find_path(dir_name, paths):
    result = []
    for path in paths:
        if dir_name in os.listdir(path):
            bingo = os.path.join(path, dir_name)
            result.append(bingo)
            print("Found at: ", bingo)

def main():
    lin=os.listdir(lin_path)
    win=multiple_paths([win_path, win_path2])

    print('These games are installed on both lin and win')
    #https://stackoverflow.com/questions/11615041/how-to-find-match-items-from-two-lists
    conflicts=set(win).intersection(set(lin))
    conflicts, ignore_count = ignore_conflicts(conflicts)
    print("Found {} conflicts ({} ignored)".format(len(conflicts), ignore_count))

    reader_buffer=5
    for id, conflict in enumerate(sorted(conflicts)):
        reader_buffer-=1
        print(conflict)
        find_path(conflict, [lin_path, win_path, win_path2])
        if reader_buffer == 0:
            input('...continue...')
            reader_buffer=5

if __name__ == '__main__':
    main()
