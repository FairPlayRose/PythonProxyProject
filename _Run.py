
from PIL import Image
from PyPDF2 import PdfFileMerger
import os
import sys
from datetime import datetime
import time

now = datetime.now()
current_time = now.strftime("%Y-%m-%d-%H%M%S")

sys.path.append(os.getcwd())

import _proxy

def Run(list_of_cards: list[str], title: None = None, window: None = None, mask_color: None = None) -> None:
    
    status_window = window["-OutText-"]
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S:%f")
    status_window.update(status_window.get() + f'\n {current_time}\n   Running')
    
    card_w = 750
    card_h = 1046
    h_margin = 95
    h_spacing = 0
    v_margin = 100
    v_spacing = 0
    pos_counter = 0
    page_counter = 0
    
    list_of_proxies = []
    
    for card in list_of_cards:
        try:
            proxy = _proxy.Proxy(card['name'], color = mask_color)
            proxy.makeQR()
        except AssertionError as e:
            print(e.__str__())
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S:%f")
            status_window.update(status_window.get() + f'\n{current_time} {e.__str__()}')
            continue
        else:
            proxyImage = proxy.Construct()
        finally:
            list_of_proxies.append({'image': proxyImage, 'quant': card['quant']})
            time.sleep(0.1)
        #    status_window.update(status_window.get() + f'\n{current_time}:\n   Fetch done for {proxy.Name}')
    
    
    PDF_titles = []
    BlankMain = Image.new(mode='RGB', size=(2480,3508), color='white')

    for proxy in list_of_proxies:
        for _ in range(0, proxy['quant']):
            if pos_counter == 9:
                BlankMain.save(f"{title}-{page_counter}.pdf","PDF")
                PDF_titles.append(f"{title}-{page_counter}.pdf")
                BlankMain = Image.new(mode='RGB', size=(2480,3508), color='white')
                page_counter += 1
                pos_counter = 0
                pass
            h_offset = h_margin + (pos_counter % 3) * (h_spacing + card_w)
            v_offset = v_margin + (pos_counter // 3) * (v_spacing + card_h)
            BlankMain.paste(proxy['image'], box = (h_offset, v_offset))
            pos_counter += 1
        
    BlankMain.save(f"{title}-{page_counter}.pdf","PDF")
    PDF_titles.append(f"{title}-{page_counter}.pdf")
    
    merger = PdfFileMerger()
        
    for pdf in PDF_titles:
        merger.append(pdf)
    
    merger.write(f"{title}.pdf")
    merger.close()
    
    for pdf in PDF_titles:
        if os.path.exists(pdf):
            os.remove(pdf)
        else:
            pass
    
    window['-RUN-'].update(disabled = False)
    window['-Cards-'].update(disabled = False)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S:%f")
    status_window.update(status_window.get() + f'\n{current_time}\n   Done')
    
    return

def scaleimage(im):
    width, height = (200, 278)
    w, h = im.size
    scale = min(width/w, height/h, 1)
    if scale != 1:
        im = im.resize((int(w*scale), int(h*scale)))
    return im

def test_build():
    pass
#    test_image_list = []
#    S
#    if bool(test_image_list):
#        test1.makeQR()
#        test2.makeQR()
#        image1 = test1.Construct()
#        image2 = test2.Construct()
#        image1 = scaleimage(image1)
#        image2 = scaleimage(image2)
#        test_image_list.append(image1)
#        test_image_list.append(image2)
#        return test_image_list
#    
#    test1 = _proxy.Proxy('Hoarding Ogre', '{3}{R}', test_id = True)
#    test2 = _proxy.Proxy('Augmenter Pugilist // Echoing Equation', '{1}{G}{G} // {3}{R}{R}', test_id = True)
#    test1.makeQR()
#    test2.makeQR()
#    image1 = test1.Construct()
#    image2 = test2.Construct()
#    image1 = scaleimage(image1)
#    image2 = scaleimage(image2)
#    test_image_list.append(image1)
#    test_image_list.append(image2)
#    return test_image_list