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
if get_sizes:
    thorough_size_compare = True
    if thorough_size_compare:
        total_non_ignored_used = True


def process_paths(paths):
    """verify that all paths exist, expands ~ too
    returns ok paths for windows and linux (depends on just path_name)"""
    ok_paths = {}

    for path_name, path in paths.items():
        # ~ path
        if path.startswith('~'):
            expanded = os.path.expanduser(path)
            if not os.path.exists(expanded):
                print(f"ERROR: {expanded} not found, skipping")
                continue
            ok_paths[path_name] = expanded
        # regular path
        else:
            if not os.path.exists(path):
                print(f"ERROR: {path_name} not found, skipping")
                continue
            ok_paths[path_name] = path

    # split by path_name
    lin_paths = []
    win_paths = []
    for path_name, path in ok_paths.items():
        if path_name.startswith('lin'):
            lin_paths.append(path)
        elif path_name.startswith('win'):
            win_paths.append(path)

    return lin_paths, win_paths


def listdir_multiple_paths(paths):
    "append each item for result of listdir"
    return [listed_dir
            for path in paths
            for listed_dir in os.listdir(path)]


def load_ignore_conflicts_list():
    "load a ignore file with some filtering (skip # and empty)"
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


def get_dir_sizes(*paths):
    result = []
    for path in paths:
        result.append(get_dir_size(path))
    return result



def main():
    "scan paths, highglights conflicts, display on buffered way"
    lin_paths, win_paths = process_paths(PATHS)
    all_paths = lin_paths + win_paths

    lin=listdir_multiple_paths(lin_paths)
    win=listdir_multiple_paths(win_paths)
    ignore_list = load_ignore_conflicts_list()

    print('These games are installed on both lin and win')
    #https://stackoverflow.com/questions/11615041/how-to-find-match-items-from-two-lists
    conflicts=set(win).intersection(set(lin))
    print("Found {} conflicts.".format(len(conflicts)))

    if total_non_ignored_used:
        total_size = 0
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
            if thorough_size_compare:
                print("Sizes:")
                for size in get_dir_sizes(*paths):
                    if total_non_ignored_used:
                        total_size += size
                    print(f" {round(float(size)/1024/1024/1024, 3)} GB")
            else:
                # get dir for just one of the paths
                print(f"Size: {round(float(get_dir_size(paths[0]))/1024/1024/1024, 3)} GB")
        else:
            find_path(conflict, all_paths)
        if reader_buffer == 0:
            input('...continue...')
            reader_buffer=5

    print("Found {} conflicts ({} ignored.)".format(len(conflicts), ignore_count))
    if total_non_ignored_used:
        print(f"Total space used by having one game installed at two places: {total_size/1024/1024/1024} GB")

if __name__ == '__main__':
    main()
