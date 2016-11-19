# -*- coding: utf-8 -*- 
#    This file is part of pyg15daemon.
#
#    pyg15daemon is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    pyg15daemon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyg15daemon; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#    (c) 2006 Sven Ludwig
#
#    This is the python binding for the g15daemon written by Mike Lampard,
#    Philip Lawatsch, and others.
"""Python binding for g15daemon

available at http://g15daemon.sf.net

This script will be available at http://abraumhal.de/
"""

import socket, time, math
import struct

from freetype import FT_Exception, Face
from freetype.ft_enums import *

from .fontdata6x4 import *
from .fontdata7x5 import *
from .fontdata8x8 import *

SCREEN_PIXEL=0
"""Setup a pixel buffer"""
SCREEN_TEXT=1
"""Setup a text buffer"""
SCREEN_WBMP=2
"""Setup a wbmp buffer"""

BYTE_SIZE=8

MAX_X=160
"""Maximum x axis resolution"""
MAX_Y=43
"""Maximum y axis resolution"""
MAX_BUFFER_LENGTH=MAX_X*MAX_Y
"""Maximum buffer length"""

PIXEL_ON=chr(1)
"""Pixel which is set or on"""
PIXEL_OFF=chr(0)
"""Pixel which is unset or off"""

G15_TEXT_SMALL=0
G15_TEXT_MED=1
G15_TEXT_LARGE=2
G15_MAX_FACE=5

G15DAEMON_KEY_HANDLER = 0x10
G15DAEMON_SWITCH_PRIORITIES = 0x70
G15DAEMON_NEVER_SELECT = 0x6e

G15_KEY_L1 = 1 << 22
G15_KEY_L2 = 1 << 23
G15_KEY_L3 = 1 << 24
G15_KEY_L4 = 1 << 25
G15_KEY_L5 = 1 << 26

G15_KEY_LIGHT = 1 << 27

def loader_ascii_10_format(file):
    """
    Loads data from file which is formated in the following way:
        11101101011...

    it the length must be 4800 chars
    """
    buf=open(file).read()
    nbuf=''
    for i in range(0,len(buf)):
        if buf[i] == '0' or buf[i] == '1':
            nbuf+=chr(ord(buf[i])-48)
    return nbuf

class g15screen:
    """
    G15daemon communication class
    """

    def __init__(self,screentype,host='localhost',port=15550):
        """
        screentype uses these variables:
            SCREEN_PIXEL, SCREEN_TEXT and SCREEN_WBMP
        host:
            g15daemon listening host
        port:
            g15daemon listening port
        """
        if screentype == SCREEN_PIXEL:
            self.init_string=b"GBUF"
        elif screentype == SCREEN_TEXT:
            self.init_string=b"TBUF"
        elif screentype == SCREEN_WBMP:
            self.init_string=b"WBUF"
        self.remote_host=host
        self.remote_port=port
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_OOBINLINE, 1)
        self.socket.connect((self.remote_host, self.remote_port))
        if self.socket.recv(16).decode('utf-8') != "G15 daemon HELLO":
            raise Exception("Communication error with server")
        self.socket.send(self.init_string)
        self.clear()
        
        self.ttf_face = []
        self.ttf_fontsize = []

        self.rotcount = 0

    def request_key_handler(self):
        if self.socket:
            self.socket.send(bytes([G15DAEMON_KEY_HANDLER]), socket.MSG_OOB)
    
    def get_key(self):
        if self.socket:
            ret = self.socket.recv(8)
            if ret is None:
                return None

            if len(ret) == 8:
                return struct.unpack("I", ret[0:4])[0]

        #this happens also, if the socket was shut down before we received the 8 Bytes
        return None

    def close(self):
        """
        Close socket
        """
        if self.socket:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
            self.socket = None

    def __del__(self):
        self.close()

    def __validate_buffer(self,buf, use_exceptions):
        """
        Validate given buffer
        """
        if len(buf) != MAX_BUFFER_LENGTH:
            if use_exceptions:
                raise Exception("Buffer has wrong size(%d)" % len(buf))
            return False
        for i in range(0,MAX_BUFFER_LENGTH):
            if not self.__validate_pixel(buf[i]):
                if use_exceptions:
                    raise Exception("Buffer contains at position %d an invalid char" % i)
                return False
        self.screen=str(buf)
        return True

    def __validate_pixel(self,pixel):
        """
        Validate given pixel
        """
        return pixel==PIXEL_OFF or pixel==PIXEL_ON

    def clear(self):
        self.screen=''
        for i in range(0,MAX_BUFFER_LENGTH):
            self.screen+=PIXEL_OFF
        
    def load(self, file,loader_function, use_exceptions=True):
        """Loads a pixmap from a file using a given loader funktion"""
        buf=loader_function(file)
        return self.__validate_buffer(buf,use_exceptions)

    def set_buffer(self, buf, use_exceptions=True):
        """
        Set a new buffer
        """
        return self.__validate_buffer(buf,use_exceptions)

    def set_pixel(self, x, y, pixel):
        """
        Set a pixel in buffer
        """
        if pixel == 1:
            pixel = PIXEL_ON
        elif pixel == 0:
            pixel = PIXEL_OFF
        if not self.__validate_pixel(pixel):
            print("nope: %s" % pixel)
            return False
        if x < 0 or x >= MAX_X:
            return False
        if y < 0 or y >= MAX_Y:
            return False
        position=x+y*MAX_X
        if x == 0 and y == 0:
            self.screen='%s%s' % (pixel,self.screen[1:])
        elif y == MAX_Y - 1 and x == MAX_X -1:
            self.screen='%s%s' % (self.screen[:-1],pixel)
        else:
            self.screen='%s%s%s' % (
              self.screen[:position],
              pixel,
              self.screen[position+1:]
            )
            
    def get_pixel(self, x, y):
        if x < 0 or x >= MAX_X:
            return -1
        if y < 0 or y >= MAX_Y:
            return -1
        position = x + y * MAX_X
        
        return self.screen[position]

    def render_character_large(self, col, row, character, sx, sy):
        helper = ord(character) * 8	# for our font which is 8x8 

        top_left_pixel_x = sx + col * (8)	# 1 pixel spacing 
        top_left_pixel_y = sy + row * (8)	# once again 1 pixel spacing 

        for y in range(0, 8):
            for x in range(0,8):
                if helper + y >= len(fontdata_8x8):
                    helper = ord('x')

                font_entry = fontdata_8x8[helper + y]
                
                if font_entry & 1 << (7 - x):
                    self.set_pixel(top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_ON)
                else:
                    self.set_pixel(top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_OFF)

    def render_character_medium(self, col, row, character, sx, sy):
        helper = ord(character) * 7 * 5 # for our font which is 6x4 

        top_left_pixel_x = sx + col * (5)	# 1 pixel spacing 
        top_left_pixel_y = sy + row * (7)	# once again 1 pixel spacing 

        for y in range(0, 8):
            for x in range(0, 6):
                if helper + y * 5 + x >= len(fontdata_7x5):
                    helper = ord('x')

                font_entry = fontdata_7x5[helper + y * 5 + x]

                if font_entry != 0:
        	        self.set_pixel (top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_ON)
                else:
	                self.set_pixel(top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_OFF)

    def render_character_small(self, col, row, character, sx, sy):
        helper = ord(character) * 6 * 4	# for our font which is 6x4

        top_left_pixel_x = sx + col * (4)	# 1 pixel spacing 
        top_left_pixel_y = sy + row * (6)	# once again 1 pixel spacing 

        for y in range(0, 7):
            for x in range(0, 5):
                if helper + y * 4 + x >= len(fontdata_6x4):
                    helper = ord('x')

                font_entry = fontdata_6x4[helper + y * 4 + x]

                if font_entry != 0:
                    self.set_pixel(top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_ON)
                else:
                    self.set_pixel(top_left_pixel_x + x, top_left_pixel_y + y, PIXEL_OFF)

    @staticmethod
    def max_characters_in_row(size):
        if size == G15_TEXT_SMALL:
            return 40
        elif size == G15_TEXT_MED:
            return 32
        elif size == G15_TEXT_LARGE:
            return 20

    def rotate(self, instr, maxsize, suffix):
        outstr = instr.strip()
        if len(outstr) <= maxsize:
            return outstr

        outstr += suffix
        offset = self.rotcount % len(outstr)
        first = outstr[offset:maxsize + offset]

        self.rotcount = (self.rotcount + 1) % 1000

        if len(first) < maxsize:
            first += " " + outstr[:maxsize - len(first) - 1]

        return first

    def render_string(self, stringOut, row, size, sx, sy, rotate=False, rotateSuffix=" ---"):
        if rotate:
            stringOut = self.rotate(stringOut, self.max_characters_in_row(size), rotateSuffix)

        for i, c in enumerate(stringOut):
            if size == G15_TEXT_SMALL:
                self.render_character_small(i, row, c, sx, sy)
            elif size == G15_TEXT_MED:
                self.render_character_medium(i, row, c, sx, sy)
            elif size == G15_TEXT_LARGE:
                self.render_character_large(i, row, c, sx, sy)

    def display(self):
        """
        Show current buffer on display
        """
        if self.socket:
            self.socket.send(bytes(self.screen, 'utf-8'))

    def ttf_load(self, fontname, fontsize):
        """
        Loads a font by the full path fontname with fontsize.
        Returns a tuple (errorcode, id of the loaded font)
        """
        try:
            newface = Face(fontname, 0)
        except FT_Exception as exc:
            return (exc.errcode, -1)
        
        id = len(self.ttf_face)
        self.ttf_face.append(newface)
        
        if fontsize == 0:
            self.ttf_fontsize.append(10)
        else:
            self.ttf_fontsize.append(fontsize)

        if newface.is_scalable:
            try:
                newface.set_char_size(0, self.ttf_fontsize[id] * 64, 90, 0)
            except FT_Exception as exc:
                return (exc.errcode, id)
                
        return (0, id)

    def calc_ttf_true_ypos(self, face, y, ttf_fontsize):
        if not face.is_scalable:
            ttf_fontsize = face.available_sizes[0].height
            
        y += ttf_fontsize * 0.75
        
        return y

    def calc_ttf_totalstringwidth(self, face, string):
        slot = face.glyph
        width = 0
        
        for c in string:
            glyph_index = face.get_char_index(c)
            errcode = face.load_glyph(glyph_index, 0)
            width += slot.advance.x >> 6
            
        return width

    def calc_ttf_centering(self, face, string):
        leftpos = 80 - (self.calc_ttf_totalstringwidth(face, string) / 2)
        if leftpos < 1:
            leftpos = 1
            
        return leftpos

    def calc_ttf_right_justify(self, face, string):
        leftpos = 160 - self.calc_ttf_totalstringwidth(face, string)
        if leftpos < 1:
            leftpos = 1
            
        return leftpos
            
    def draw_ttf_char(self, charbitmap, character, x, y, color):
        x_max = x + charbitmap.width
        y_max = y + charbitmap.rows
        
        tmpbuffer = charbitmap.convert(1)
        
        q = 0
        char_y = y
        while char_y < y_max:
            p = 0
            char_x = x
            while char_x < x_max:
                if tmpbuffer.buffer[q * tmpbuffer.width + p] != 0:
                    self.set_pixel(int(char_x), int(char_y), color)
                p += 1
                char_x += 1
                
            q += 1
            char_y += 1
      
    def draw_ttf_str(self, string, x, y, color, face):
        slot = face.glyph
        
        for c in string:
            try:
                face.load_char(c, FT_LOAD_RENDER | FT_LOAD_MONOCHROME | FT_LOAD_TARGET_MONO)
            except FT_Exception as exc:
                continue
            
            self.draw_ttf_char(slot.bitmap, c, x + slot.bitmap_left, y - slot.bitmap_top, color)
            x += slot.advance.x >> 6

    def ttf_print(self, x, y, fontsize, face_num, color, center, print_string):
        if self.ttf_fontsize[face_num] != 0:
            if fontsize > 0 and self.ttf_face[face_num].is_scalable:
                self.ttf_fontsize[face_num] = fontsize
                try:
                    self.ttf_face[face_num].set_pixel_sizes(0, self.ttf_fontsize[face_num])
                except FT_Exception as exc:
                    print("Trouble setting the Glyph size: %d" % exc.errcode)

            y = self.calc_ttf_true_ypos(self.ttf_face[face_num], y, self.ttf_fontsize[face_num])
            if center == 1:
                x = self.calc_ttf_centering(self.ttf_face[face_num], print_string)
            elif center == 2:
                x = self.calc_ttf_right_justify(self.ttf_face[face_num], print_string)
                
            self.draw_ttf_str(print_string, x, y, color, self.ttf_face[face_num])

    def pixel_reverse_fill(self, x1, y1, x2, y2, fill, color):
        """
        The area with an upper left corner at (x1, y1) and lower right corner at (x2, y2) will be
        filled with color if fill>0 or the current contents of the area will be reversed if fill==0.
 
        \param x1 Defines leftmost bound of area to be filled.
        \param y1 Defines uppermost bound of area to be filled.
        \param x2 Defines rightmost bound of area to be filled.
        \param y2 Defines bottommost bound of area to be filled.
        \param fill Area will be filled with color if fill != 0, else contents of area will have color values reversed.
        \param color If fill != 0, then area will be filled if color == 1 and emptied if color == 0.
        """
        for x in range(x1, x2 +1):
            for y in range(y1, y2 +1):
                if not fill:
                    color = self.get_pixel(x, y)
                self.set_pixel(x, y, color)

    def pixel_overlay(self, x1, y1, width, height, colormap):
        """
        A 1-bit bitmap defined in colormap[] is drawn to the canvas with an upper left corner at (x1, y1)
        and a lower right corner at (x1+width, y1+height).
        
        \param x1 Defines the leftmost bound of the area to be drawn.
        \param y1 Defines the uppermost bound of the area to be drawn.
        \param width Defines the width of the bitmap to be drawn.
        \param height Defines the height of the bitmap to be drawn.
        \param colormap An array containing width*height entries of value 0 for pixel off or != 0 for pixel on.
        """
        for i in range(0, width * height):
            color = PIXEL_ON if colormap[i] != 0 else PIXEL_OFF
            x = x1 + i % width
            y = int(y1 + i / width)
            self.set_pixel(x, y, color)

    def draw_line(self, px1, py1, px2, py2, color):
        """
        A line of color is drawn from (px1, py1) to (px2, py2).
        
        \param px1 X component of point 1.
        \param py1 Y component of point 1.
        \param px2 X component of point 2.
        \param py2 Y component of point 2.
        \param color Line will be drawn this color.
        """
        steep = False
        
        if abs(py2 - py1) > abs(px2 - px1):
            steep = True
        
        if steep:
            px1, py1 = py1, px1
            px2, py2 = py2, px2
            
        if px1 > px2:
            px1, px2 = px2, px1
            py1, py2 = py2, py1
            
        dx = px2 - px1
        dy = abs(py2 - py1)
        
        error = 0
        y = py1
        ystep = 1 if py1 > py2 else -1
        
        for x in range(0, px2 +1):
            if steep:
                self.set_pixel(y, x, color)
            else:
                self.set_pixel(x, y, color)
            
            error += dy
            if 2 * error >= dx:
                y += ystep
                error -= dx

    def pixel_box(self, x1, y1, x2, y2, color, thick, fill):
        """
        Draws a box around the area bounded by (x1, y1) and (x2, y2).
        
        The box will be filled if fill != 0 and the sides will be thick pixels wide.
        
        \param x1 Defines leftmost bound of the box.
        \param y1 Defines uppermost bound of the box.
        \param x2 Defines rightmost bound of the box.
        \param y2 Defines bottommost bound of the box.
        \param color Lines defining the box will be drawn this color.
        \param thick Lines defining the box will be this many pixels thick.
        \param fill The box will be filled with color if fill != 0.
        """
        for i in range(0, thick):
            self.draw_line(x1, y1, x2, y1, color)
            self.draw_line(x1, y1, x1, y2, color)
            self.draw_line(x2, y1, x2, y2, color)
            self.draw_line(x1, y2, x2, y2, color)
            x1 += 1
            y1 += 1
            x2 -= 1
            y2 -= 1
        
        if fill:
            for x in range(x1, x2 +1):
                for y in range(y1, y2 +1):
                    self.set_pixel(x, y, color)

    def draw_circle(self, x, y, r, fill, color):
        """
        Draws a circle centered at (x, y) with a radius of r.
        
        The circle will be filled if fill != 0.
        
        \param x Defines horizontal center of the circle.
        \param y Defines vertical center of circle.
        \param r Defines radius of circle.
        \param fill The circle will be filled with color if fill != 0.
        \param color Lines defining the circle will be drawn this color.
        """
        xx = 0
        yy = r
        dd = 2 * (1 - r)
        
        while yy >= 0:
            if not fill:
                self.set_pixel(x + xx, y - yy, color)
                self.set_pixel(x + xx, y + yy, color)
                self.set_pixel(x - xx, y - yy, color)
                self.set_pixel(x - xx, y + yy, color)
            else:
                self.draw_line(x - xx, y - yy, x + xx, y - yy, color)
                self.draw_line(x - xx, y + yy, x + xx, y + yy, color)
            
            if dd + yy > 0:
                yy -= 1
                dd = dd - (2 * yy +1)
            
            if xx > dd:
                xx += 1
                dd = dd + (2 * xx +1)

    def draw_round_box(self, x1, y1, x2, y2, fill, color):
        """
        Draws a rounded box around the area bounded by (x1, y1) and (x2, y2).
        
        The box will be filled if fill != 0.
        
        \param x1 Defines leftmost bound of the box.
        \param y1 Defines uppermost bound of the box.
        \param x2 Defines rightmost bound of the box.
        \param y2 Defines bottommost bound of the box.
        \param fill The box will be filled with color if fill != 0.
        \param color Lines defining the box will be drawn this color.
        """
        shave = 3
        
        if shave > (x2 - x1) / 2:
            shave = (x2 - x1) / 2
        if shave > (y2 - y1) / 2:
            shave = (y2 - y1) / 2
        
        if x1 != x2 and y1 != y2:
            if fill:
                self.draw_line(x1 + shave, y1, x2 - shave, y1, color)
                for y in range(y1 +1, y1 + shave):
                    self.draw_line(x1 +1, y, x2 -1, y, color)
                for y in range(y1 + shave, y2 - shave +1):
                    self.draw_line(x1, y, x2, y, color)
                for y in range(y2 - shave +1, y2):
                    self.draw_line(x1 +1, y, x2 -1, y, color)
                self.draw_line(x1 + shave, y2, x2 - shave, y2, color)
                if shave == 4:
                    self.set_pixel(x1 +1, y1 +1, PIXEL_ON if color == PIXEL_OFF else PIXEL_OFF)
                    self.set_pixel(x1 +1, y2 -1, PIXEL_ON if color == PIXEL_OFF else PIXEL_ON)
            else:
                self.draw_line(x1 + shave, y1, x2 - shave, y1, color)
                self.draw_line(x1, y1 + shave, x1, y2 - shave, color)
                self.draw_line(x2, y1 + shave, x2, y2 - shave, color)
                self.draw_line(x1 + shave, y2, x2 - shave, y2, color)
                if shave > 1:
                    self.draw_line(x1 + 1, y1 + 1, x1 + shave - 1, y1 + 1, color)
                    self.draw_line(x2 - shave + 1, y1 + 1, x2 - 1, y1 + 1, color)
                    self.draw_line(x1 + 1, y2 - 1, x1 + shave - 1, y2 - 1, color)
                    self.draw_line(x2 - shave + 1, y2 - 1, x2 - 1, y2 - 1, color)
                    self.draw_line(x1 + 1, y1 + 1, x1 + 1, y1 + shave - 1, color)
                    self.draw_line(x1 + 1, y2 - 1, x1 + 1, y2 - shave + 1, color)
                    self.draw_line(x2 - 1, y1 + 1, x2 - 1, y1 + shave - 1, color)
                    self.draw_line(x2 - 1, y2 - 1, x2 - 1, y2 - shave + 1, color)

    def draw_bar(self, x1, y1, x2, y2, color, num, maxu, btype):
        """
        Given a maximum value, and a value between 0 and that maximum value, calculate and draw a bar showing that percentage.
        
        \param x1 Defines leftmost bound of the bar.
        \param y1 Defines uppermost bound of the bar.
        \param x2 Defines rightmost bound of the bar.
        \param y2 Defines bottommost bound of the bar.
        \param color The bar will be drawn this color.
        \param num Number of units relative to max filled.
        \param max Number of units equal to 100% filled.
        \param type Type of bar.  1=solid bar, 2=solid bar with border, 3 = solid bar with I-frame.
        """
        if maxu == 0:
            return
        
        if num > maxu:
            num = maxu
            
        if btype == 2:
            y1 += 2
            y2 -= 2
            x1 += 2
            x2 -= 2
            
        leng = maxu / num
        length = (x2 - x1) / leng
        
        if btype == 1:
            self.pixel_box(x1, y1 - btype, x2, y2 + btype, color ^ 1, 1, 1)
            self.pixel_box(x1, y1 - btype, x2, y2 + btype, color, 1, 0)
        elif btype == 2:
            self.pixel_box(x1 -2, y1 - btype, x2 +2, y2 + btype, color ^ 1, 1, 1)
            self.pixel_box(x1 -2, y1 - btype, x2 +2, y2 + btype, color, 1, 0)
        elif btype == 3:
            self.draw_line(x1, y1 - btype, x1, x2 + btype, color)
            self.draw_line(x2, y1 - btype, x2, y2 + btype, color)
            self.draw_line(x1, y1 + ((y2 - y1) / 2), x2, y1 + ((y2 - y1) / 2), color)
        
        self.pixel_box(x1, y1, math.ceil(x1 + length), y2, color, 1, 1)

    def load_wbmp_splash(self, filename):    
        """
        wbmp splash screen loader - assumes image is 160x43
        
        \param filename A string holding the path to the wbmp to be displayed.
        """
        (width, height, buf) = self.load_wbmp_to_buf(filename)
        self.draw_icon(buf, 0, 0, width, height)

    def draw_icon(self, buf, my_x, my_y, width, height):
        """
        Draw an icon to a canvas 
        
        \param buf A pointer to the buffer holding the icon to be displayed.
        \param my_x Leftmost boundary of image.
        \param my_y Topmost boundary of image.
        \param width Width of the image in buf.
        \param height Height of the image in buf.
        """
        for y in range(0, height -1):
            for x in range(0, width -1):
                pixel_offset = y * width + x
                byte_offset = int(pixel_offset / BYTE_SIZE)
                bit_offset = 7 - (pixel_offset % BYTE_SIZE)
                
                val = (buf[byte_offset] & (1 << bit_offset)) >> bit_offset
                self.set_pixel(x + my_x, y + my_y, chr(val))

    def draw_sprite(self, buf, my_x, my_y, width, height, start_x, start_y, total_width):
        """
        Draw a sprite to a canvas

        \param buf A pointer to the buffer holding a set of sprites.
        \param my_x Leftmost boundary of image.
        \param my_y Topmost boundary of image.
        \param width Width of the sprite.
        \param height Height of the sprite.
        \param start_x X offset for reading sprite from buf.
        \param start_y Y offset for reading sprite from buf.
        \param total_width Width of the set of sprites held in buf.
        """        
        for y in range(0, height -1):
            for x in range(0, width -1):
                pixel_offset = (y + start_y) * total_width + (x + start_x)
                byte_offset = int(pixel_offset / BYTE_SIZE)
                bit_offset = 7 - (pixel_offset % BYTE_SIZE)
                
                val = (buf[byte_offset] & (1 << bit_offset)) >> bit_offset
                self.set_pixel(x + my_x, y + my_y, chr(val))

    def load_wbmp_to_buf(self, filename):
        """
        basic wbmp loader - loads a wbmp image into a buffer.
        
        \param filename A string holding the path to the wbmp to be loaded.
        \param img_width A pointer to an int that will hold the image width on return.
        \param img_height A pointer to an int that will hold the image height on return.
        @return: (img_width, img_height, buf) or (0, 0, None) on error
        """
        buflen = header = 4
        pixel_offset = 0
        
        with open(filename, "rb") as f:
            headerbytes = bytearray(f.read(5))
            
            if len(headerbytes) == 5:
                if headerbytes[2] & 1:
                    img_width = (headerbytes[2] ^ 1) | headerbytes[3]
                    img_height = headerbytes[4]
                    header = 5
                else:
                    img_width = headerbytes[2]
                    img_height = headerbytes[3]
            else:
                return (0, 0, None)
                
            byte_width = img_width / 8
            if img_width % 8:
                byte_width += 1
                
            buflen = byte_width * img_height
            
            if header == 4:
                buf = bytearray(headerbytes[4])
            else:
                buf = bytearray()
             
            for b in f.read():
                buf.append(b)   
            #buf += f.read()
            
        for y in range(0, img_height):
            for x in range(0, img_width):
                pixel_offset = y * img_width + x
                byte_offset = int(pixel_offset / BYTE_SIZE)
                bit_offset = 7 - (pixel_offset % BYTE_SIZE)

                val = (buf[byte_offset] & (1 << bit_offset)) >> bit_offset
                
                if not val:
                    buf[byte_offset] = buf[byte_offset] | 1 << bit_offset
                else:
                    buf[byte_offset] = buf[byte_offset] & ~(1 << bit_offset)
                    
        return (img_width, img_height, buf)

    def draw_big_num(self, x1, y1, x2, y2, color, num):
        """
        Draw a large number to a canvas
        
        \param x1 Defines leftmost bound of the number.
        \param y1 Defines uppermost bound of the number.
        \param x2 Defines rightmost bound of the number.
        \param y2 Defines bottommost bound of the number.
        \param num The number to be drawn.
        """
        x1 += 2
        x2 -= 2
        
        if num == 0:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1 +5, y1 +5, x2 -5, y2 -6, 1 - color, 1, 1)
        elif num == 1:
            self.pixel_box(x2 -5, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1, y1, x2 -5, 1 - color, 1, 1)
        elif num == 2:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1, y1 +5, x2 -5, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1 +5, y1 + int((y2 / 2) +3), x2, y2 -6, 1 - color, 1, 1)
        elif num == 3:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1, y1 +5, x2 -5, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1, y1 + int((y2 / 2) +3), x2 -5, y2 -6, 1 - color, 1, 1)
        elif num == 4:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1, y1 + int((y2 / 2) +3), x2 -5, y2, 1 - color, 1, 1)
            self.pixel_box(x1 +5, y1, x2 -5, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
        elif num == 5:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1 +5, y1 +5, x2, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1, y1 + int((y2 / 2) +3), x2 -5, y2 -6, 1 - color, 1, 1)        
        elif num == 6:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1 +5, y1 +5, x2, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1 +5, y1 + int((y2 / 2) +3), x2 -5, y2 -6, 1 - color, 1, 1)
        elif num == 7:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1, y1 +5, x2 -5, y2, 1 - color, 1, 1)
        elif num == 8:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1 +5, y1 +5, x2 -5, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1 +5, y1 + int((y2 / 2) +3), x2 -5, y2 -6, 1 - color, 1, 1)
        elif num == 9:
            self.pixel_box(x1, y1, x2, y2, color, 1, 1)
            self.pixel_box(x1 +5, y1 +5, x2 -5, y1 + int((y2 / 2) -3), 1 - color, 1, 1)
            self.pixel_box(x1, y1 + int((y2 / 2) +3), x2 -5, y2, 1 - color, 1, 1)
        elif num == 10:
            self.pixel_box(x2 -5, y1 +5, x2, y1 +10, color, 1, 1)
            self.pixel_box(x2 -5, y2 -10, x2, y2 -5, color, 1, 1)
        elif num == 11:
            self.pixel_box(x1, y1 + int((y2 / 2) -2), x2, y1 + int((y2 / 2) +2), color, 1, 1)
        elif num == 12:
            self.pixel_box(x2 -5, y2 -5, x2, y2, color, 1, 1)
    
    
if __name__ == "__main__":
    g15=g15screen(SCREEN_PIXEL)
    try:
        open('lcd.ascii')
        file=True
    except:
        file=False
    if file:
        g15.load('lcd.ascii',loader_ascii_10_format)
        g15.display()
        time.sleep(1)
        for y in range(MAX_Y):
            for x in range(MAX_X+1):
                g15.set_pixel(x,y, PIXEL_ON)
            g15.display()
            time.sleep(0.2)
    else:
        g15.clear()
        """for i in range(MAX_X):
            g15.set_pixel(i,0, PIXEL_ON)
            g15.set_pixel(i,MAX_Y-1, PIXEL_ON)

            if i>4 and i<MAX_X-5:
                g15.set_pixel(i,5, PIXEL_ON)
                g15.set_pixel(i,MAX_Y-6, PIXEL_ON)

            if i < MAX_Y:
                g15.set_pixel(0,i, PIXEL_ON)
                g15.set_pixel(MAX_X-1,i, PIXEL_ON)

                if i > 5 and i < MAX_Y -5:
                    g15.set_pixel(5,i, PIXEL_ON)
                    g15.set_pixel(MAX_X-6,i, PIXEL_ON)"""
        (err, ind) = g15.ttf_load(b'./unifont.ttf', 10)
        if err == 0:
            print("loaded: %d" % ind)
            g15.ttf_print(0, 0, 20, ind, PIXEL_ON, 1, "muh")#"てんㆁㅆㄤ!")
        else:
            print("error: %s" % err)
        
        #g15.draw_big_num(0, 0, 0, 0, 1, 4)
        #g15.draw_circle(110, 21, 15, 1, 1)
        #(width, height, buf) = g15.load_wbmp_to_buf("./splash.wbmp")
        #if buf != None:
        #if True:
            #print("width: %s, height: %s" % (width, height))
            #g15.load_wbmp_splash("./splash.wbmp")
            #g15.draw_sprite(buf, 0, 0, width, height, 0, 0, width)
            #(self, buf, my_x, my_y, width, height, start_x, start_y, total_width):
            #g15.draw_sprite(buf, 30, 10, 43, 20, 30, 10, width);
            #g15.draw_sprite(buf, 10, 20, 15, 20, 10, 20, width);
            #g15.draw_sprite(buf, 100, 20, 25, 20, 100, 20, width);
            #g15.draw_icon(buf, 0, 0, width, height)
        
        g15.display()
        g15.keystate()
    time.sleep(5)
    del(g15)
