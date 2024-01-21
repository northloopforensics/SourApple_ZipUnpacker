import PySimpleGUI as sg
from zipfile import ZipFile, BadZipFile
import os

# def unpack_zip(zipfile='', path_from_local=''):
#     filepath = path_from_local+zipfile
#     extract_path = filepath.strip('.zip')+'/'
#     parent_archive = ZipFile(filepath)
#     parent_archive.extractall(extract_path)
#     namelist = parent_archive.namelist()
#     parent_archive.close()
#     for name in namelist:
#         try:
#             if name[-4:] == '.zip':
#                 unpack_zip(zipfile=name, path_from_local=extract_path)
#         except:
#             print('failed on', name)
#             pass
#     return extract_path
    
def unpack_zip(zipfile='', path_from_local=''):
    filepath = path_from_local + zipfile
    extract_path = filepath.strip('.zip') + '/'

    try:
        with ZipFile(filepath, 'r') as parent_archive:
            parent_archive.extractall(extract_path)
            namelist = parent_archive.namelist()

            for name in namelist:
                if name.lower().endswith('.zip'):
                    try:
                        unpack_zip(zipfile=name, path_from_local=extract_path)
                    except BadZipFile:
                        print(f'Skipping {name} - Not a valid zip file')

    except BadZipFile:
        print(f'Skipping {zipfile} - Not a valid zip file')
    except IsADirectoryError:
        print(f'Skipping {zipfile} - Is a directory')

    return extract_path

# PySimpleGUI layout
layout = [
    [sg.Text('Select a folder containing zip files to unpack:')],
    [sg.InputText(key='folder_path', size=(50, 1)), sg.FolderBrowse()],
    [sg.Button('Unpack'), sg.Button('Exit')],
]

window = sg.Window('SourApple: Zip File Unpacker', layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Unpack':
        Folder_path = values['folder_path']
        if Folder_path:
            try:
                folder_contents = os.listdir(Folder_path)
                fullpaths = [os.path.join(Folder_path, item) for item in folder_contents]
                for thingy in fullpaths:
                    extract_path = unpack_zip(zipfile=thingy)
                sg.popup(f'Success!')
            except Exception as e:
                sg.popup_error(f'Error: {str(e)}')

window.close()
