def remove_all_from_directory():
    print('hello from remove_from_directory')


def remove(file_to_delete):
    import os
    # just as a check, only remove files that end with .mp3
    if(file_to_delete[-4:] == ".mp3"):
        os.remove(file_to_delete)
        print('removed: ' + file_to_delete)

