import os
from pprint import pprint as pp

PATHS={
    'win_path':'/masterstorage/steamlibrary_win_only/SteamLibrary/steamapps/common/',
    'lin_path':'/motherstorage/SteamLibrary/steamapps/common/',
    'lin_path2':'~/.local/share/Steam/steamapps/common',
    'win_path2':'/mnt/Program Files (x86)/Steam/steamapps/common/',
}
IGNORE_CONFLICTS_FILE='ignore_conflicts.txt'
get_sizes = True

def process_paths(paths):
    "verify that all paths exist, expands ~ too"
    ok_paths = {}

    for path_name, path in paths.items():
        if path.startswith('~'):
            expanded = os.path.expanduser(path)
            if not os.path.exists(expanded):
                print(f"ERROR: {expanded} not found, skipping")
            ok_paths[path_name] = expanded
            continue

        if not os.path.exists(path):
            print(f"ERROR: {path_name} not found, skipping")
        ok_paths[path_name] = path
    return ok_paths


def listdir_multiple_paths(paths):
    "simple append for listdir"
    result = []
    for path in paths:
        if not len(path) > 1:
            continue
        for dir_name in os.listdir(path):
            result.append(dir_name)
    return result


def load_ignore_conflicts_list():
    "load a file with some filtering"
    ignore_list = []
    if os.path.exists(IGNORE_CONFLICTS_FILE):
        with open(IGNORE_CONFLICTS_FILE) as iow:
            ignore_list = []
            for dir_name in iow.readlines():
                if not dir_name.startswith('#') and len(dir_name) > 1:
                    ignore_list.append(dir_name.strip())
    else:
        print('No {} file, no ignoring')
    return ignore_list


def find_path(dir_name, paths):
    "do listdir per path and search string in it"
    result = []
    for path in paths:
        if dir_name in os.listdir(path):
            bingo = os.path.join(path, dir_name)
            result.append(bingo)
            print("\tFound at: ", bingo)
    return result

def find_and_print(conflict, ignore_list):
    "find an item (has to be split by ',') and return True"
    for item in ignore_list:
        if conflict == item[:item.find(',')]:
            print("- Ignoring ", item)
            return True

def get_dir_size(start_path = '.'):
    "stolen from ..."
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def main():
    "scan paths, highglights conflicts, display on buffered way"
    ok_paths=process_paths(PATHS)
    all_paths=list(ok_paths.values())
    lin=listdir_multiple_paths([path if path_name.startswith('lin') else '' for path_name, path in ok_paths.items()])
    win=listdir_multiple_paths([path if path_name.startswith('win') else '' for path_name, path in ok_paths.items()])
    ignore_list = load_ignore_conflicts_list()

    print('These games are installed on both lin and win')
    #https://stackoverflow.com/questions/11615041/how-to-find-match-items-from-two-lists
    conflicts=set(win).intersection(set(lin))
    print("Found {} conflicts.".format(len(conflicts)))

    ignore_count = 0
    reader_buffer=5
    for conflict in sorted(conflicts):
        if find_and_print(conflict, ignore_list):
            ignore_count+=1
            continue
        reader_buffer-=1
        print(f"* {conflict}")
        if get_sizes:
            paths = find_path(conflict, all_paths)
            print(f"Size: {round(float(get_dir_size(paths[0]))/1024/1024/1024, 3)} GB")  # get dir for just one of the paths
        else:
            find_path(conflict, all_paths)
        if reader_buffer == 0:
            input('...continue...')
            reader_buffer=5

    print("Found {} conflicts ({} ignored.)".format(len(conflicts), ignore_count))

if __name__ == '__main__':
    main()
