import PySimpleGUI as sg
from tkinter.filedialog import askopenfilename
import threading
import io

import os
import sys

sys.path.append(os.getcwd())

import _proxy, _Run

def scaleimage(im):
    width, height = (200, 278)
    w, h = im.size
    scale = min(width/w, height/h, 1)
    if scale != 1:
        im = im.resize((int(w*scale), int(h*scale)))
    return im

def layoutGenerator(title):
    
    select_file_tooltip = 'If you have a card file, you can put it here \ninstead of typing it in above. Please read \nthe README before use.'
    
    main_top_layout = [  
        [sg.Multiline('Imput format: \nQuantity Name \n \nExample: \n1 Swiftfoot Boots \n \nClick to Clear', size = (45,20), key = '-Cards-'), 
         sg.VerticalSeparator(), 
         sg.Multiline('', size = (20, 21), key = '-OutText-', font=('Helvetica', 9), no_scrollbar=True, autoscroll= True, disabled=True)
         ]
        ]

    main_bottom_layout_1 = [
        [sg.Text('Select file:', tooltip = select_file_tooltip ,size = (8, 0), key='-FILE-TEXT-'), 
         sg.In('', size = (35, 0), disabled = True, disabled_readonly_background_color = 'white', key='-IN1-')
         ],
        [sg.Text('PDF name:', size = (8, 0), key='-PDF-TEXT-'), 
         sg.In(f'{title}', size = (35, 0), key='-IN2-')
         ]
        ]

    main_bottom_layout_2 = [
        [sg.Button('Run', key='-RUN-'), 
         sg.Button('Edit'), 
         sg.Button('Exit', focus = True)
         ]
        ]
    
    edit_buttons =[
        [sg.Text('Edit here')],
        [sg.Button('Back')],
        [sg.Button('Submit')],
        #[sg.Button('Update', key = 'Update+Edit+')]
        ]
    
    layout_edit = [
        [sg.Column(edit_buttons),
         sg.VerticalSeparator(), 
         sg.Image(key='-Image1-', size = (200,300)),
         sg.Image(key='-Image2-', size = (200, 300))
         ]
        ]
    
    layout_main = [
        [sg.Column(main_top_layout)],
        [sg.HorizontalSeparator()],
        [sg.Column(main_bottom_layout_1), sg.Column(main_bottom_layout_2)]     
        ]
    
    col_main = sg.Column(layout_main, key = 'SCMain')
    col_edit = sg.Column(layout_edit, key = 'SCEdit', visible = False)
    
    layout = [
        [sg.Pane([col_main, col_edit], relief = sg.RELIEF_FLAT)]
        ]
    
    return layout


def ui(title):
    window = sg.Window('Python Proxy Project', layoutGenerator(title=title), size = (550,420), finalize=True)

    window['-IN1-'].bind('<Button-1>', '+Click+')
    window['-IN2-'].bind('<Return>', '+Enter+')
    window['-Cards-'].bind('<Button-1>','+Click+')
    
    filename = ''
    list_of_cards = ''
    mask_color = None
    
    have_data = False
    
    
    
    while True:             # Event Loop
        event, values = window.read(timeout = 10)
        if event == '__TIMEOUT__':
            continue
            #print(event, values)
        if event == '-IN1-+Click+':
            filename = askopenfilename(title= 'Select proxy text file:', filetypes= (('text file', '.txt'),))
            window['-IN1-'].update(f'{filename}')
        if event == '-IN2-+Enter+':
            title = values['-IN2-']
        if event == '-Cards-+Click+':
            window['-Cards-'].update('')
        if event == 'Edit':
            window['SCMain'].update(visible = False)
            window['SCEdit'].update(visible = True)    
        if event == 'Update+Edit+':
            image_list = _Run.test_build()
            image1 = image_list[0]
            image2 = image_list[1]
            bio1 = io.BytesIO()
            bio2 = io.BytesIO()
            image1.save(bio1, format = "PNG")
            image2.save(bio2, format = "PNG")
            window['-Image1-'].update(data = bio1.getvalue())
            window['-Image2-'].update(data = bio2.getvalue())
        if event == 'Back':
            window['SCMain'].update(visible = True)
            window['SCEdit'].update(visible = False)
        if event == '-RUN-':
            window['-RUN-'].update(disabled = True)
            window['-Cards-'].update(disabled = True)
            window['-OutText-'].update('')
            if filename != '':
                list_of_cards = _proxy.fromFileCards(filename)
            else:
                lineList = values['-Cards-']
                list_of_cards = _proxy.fromListCards(lineList)
            threading.Thread(target = _Run.Run, args=(list_of_cards, title, window, mask_color,), daemon=True).start()
        if event in (None, 'Exit', sg.WIN_CLOSED):
            sys.exit()

