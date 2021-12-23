# More details can be found in TechToTinker.blogspot.com 
# George Bantique | tech.to.tinker@gmail.com


# Pin assignment: fuer ESP8266
# MISO -> D6    Slaves Out Master in
# MOSI -> D7    Master out Slaves in
# SCK  -> D5    serial clock
# CS   -> D8    Chip select
import gc
import os
from machine import Pin, SoftSPI
from sdcard import SDCard

#enable garbage collection um arbeitsspeicher frei zu bekommen
gc.enable()
gc.collect()

spisd = SoftSPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
sd = SDCard(spisd, Pin(15))

print('Root directory:{}'.format(os.listdir()))
vfs = os.VfsFat(sd)
os.mount(vfs, '/sd')
print('Root directory:{}'.format(os.listdir()))
os.chdir('')
print('SD Card contains:{}'.format(os.listdir()))


# 1. To read file from the root directory:
# f = open('sample.txt', 'r')
# print(f.read())
# f.close()

# 2. To create a new file for writing:
# f = open('sample2.txt', 'w')
# f.write('Some text for sample 2')
# f.close()

# 3. To append some text in existing file:
# f = open('sample3.txt', 'a')
# f.write('Some text for sample 3')
# f.close()

# 4. To delete a file:
# os.remove('file to delete')

# 5. To list all directories and files:
# os.listdir()

# 6. To create a new folder:
# os.mkdir('sample folder')

# 7. To change directory:
# os.chdir('directory you want to open')

# 8. To delete a folder:
# os.rmdir('folder to delete')

# 9.  To rename a file or a folder:
# os.rename('current name', 'desired name')