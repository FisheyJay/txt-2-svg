# ######################################################################################################################################################
# Name:                 txt2svg.py
#                       ----------
# Author:               John Fisher
#                       ----------
# Date:                 10/24/2016      Initial Creation of production process. I am sharing this subset of logic as a learning example or as a starting
#                       ----------      point for other developers having similar requirements.
#
# Description:          This logic Converts Ascii display export files (from various proprietary software applications) to Inline SVG. It functions for
#                       a particular file format but can be fairly easily adapted for other Ascii text file formats.This logic is comprised of some
#                       file I/O and mainly, 3 functions that calculate, resize and replicate lines, rectangles and
#                       polygons with the same aspect ratio, sizing and appearance as the master. I have stripped out all sensitive and proprietary
#                       information from this code and it's associated input data file.
#
# Debugging:            Verbosity Level can be set as follows: 4 = Maximum, 3 = High, 2 = Medium, 1 = Low, 0 = None
#                       I have left some diagnostics in the form of sys.stdout.write() and print() statements in just the right spots that can be quickly
#                       uncommented to get visibility into something quickly. I personally prefer the PyCharm debugger, but if you are a newer developer,
#                       you will appreciate the simplicity. Plus I can be a little lazy and not cleanup the code so much. It is very late and I am very tired.
#
# Input File:           Example.txt - Typically, you would process an AutoCAD DXF file which is very similar in format to this Example.txt file that's
#                       included herein.
#
# Input File format:    Please see File Format Definition which can be found in the Readme.md file in this same GitHub repository
#
# Output FIle:          txt2svg.svg (see file in repo.)
#
# Coming soon:          Functions to handle the replication of Text, Arcs, custom symbols, embedded real-time updating data points via hopefully an open
#                       source xlink type data binding mechanism.
# ######################################################################################################################################################

import sys as sys
import os as os
import re

color_string = "#ff0000,#00ff00,#ffff00,#0000ff,#00ffff,#ff00ff,#ffffff,#ffb500,#a10000,#00a100,#a1a100,#0000a1,#00a1a1,#7200a1,#d1d1d1,#b5b5b5,#c60000,#00ffb5,#e4e400,#008cc6,#e9e9e9,#000072,#939393,#725000,#e400a1,#00e4a1,#c68c00,#b500ff,#686868,#0000c6,#0000e4,#005072,#007200,#007250,#007272,#0072a1,#00a172,#00a1e4,#00b5ff,#00c600,#00c68c,#00c6c6,#00e400,#00e4e4,#500072,#507200,#720000,#720050,#720072,#727200,#72a100,#8c00c6,#8cc600,#a10072,#a100a1,#c100e4,#a17200,#a1e400,#b5ff00,#c6008c,#c600c6,#c6c600,#c6c600,#e4a100,#e4a100,#e4a100,#e4a100,#e4a100,#e4a100,,,,,,,,,,,,80,,,,,,,,,,90,,,,,,,,,,100,,,,,,,,,,110,,,,,,,,,,120,,,,,,,,,,130,131,132,133,134,135,136,,,,,,"
# Build the color_list using a List Comprehension.
color_list = [str(i) for i in color_string.split(',')]
color_list[0] = "black"
color_list[134] = "none"
color_list[135] = "#FFFFFF"

dotted_or_dashed_string = "4,1 + 5,1,3,1 + 1,1 + 3,1,1,1 + 12,4 + 5,1,3,1,1,1 + 4,2,4,1,1,1"
dotted_or_dashed = [str(i) for i in dotted_or_dashed_string.split(' + ')]
for y in dotted_or_dashed:
    dotted_or_dashed_list_members = [float('%.3f' % float(j)) for j in y.split(',')]
    # print(y)
    # print(dotted_or_dashed_list_members)
    for j in dotted_or_dashed_list_members:
        vb = float('%.3f' % float(j))
        # print(vb)
        # sys.stdout.write('%.3f' % vb + '\n\n')

# Verbosity: 4=Maximum, 3=High, 2=Medium, 1=Low, 0= None
VERBOSITY_LEVEL = 0
ROOTDIR = 'C:\\Users\\John\\Desktop\\rewrite'
FS = ","
START_count = 0
image_table_count = 0
sec = 0
ymult = 1
xmult = 1
lower_left_x1_pos = 0.000000
lower_left_y1_pos = 0.000000
upper_right_x2_pos = 0.000000
upper_right_y2_pos = 0.000000
ratio = 0.000000
xwx = 0.000000
yhy = 0.000000
wx = 0.000000
hy = 0.000000
privpageno = 0
INITIAL_DIMENSION = 3500
str_float = 0.000000
str_string = ''
dname = ''
device_count = 0
bracket_count = 0

asir = {}
asi_split_string = ''
asirx = {}
asiry = {}
asirxe = {}
asirye = {}

tsi_state = {}
tsi_x = {}
tsi_y = {}
tsi_off = {}
tsi_txt = {}
tsi_value = {}

tsi_state_number = ''

page_no = 0
previous_page_no = 0
w = 0.00

SVG_SVG_HEADER = "<svg version=\"1.1\" baseProfile=\"full\" height=\"80%\" viewBox=\"0 0 9500 1625\" width=\"105%\" xmlns=\"http://www.w3.org/2000/svg\" style=\"background-color: #000\">"
SVG_POLYGON = "<polygon id=\"polygon_%s\" points=\"%s\" fill=\"%s\" stroke=\"%s\" stroke-width=\"%s\"></polygon>"
SVG_G_LINE = "<g id=\"Line_%s\">"
SVG_G_CLOSE = "</g>"
SVG_SVG_DEF = "<defs>"
SVG_SVG_DEF_CLOSE = "</defs>"
SVG_SVG_HEADER_CLOSE = "</svg>"
o = ''
s = ''
ds = ''
tlqo = ''
ho = ''
ob = ''

SVG_G_LINE_COUNT = 0
SVG_G_RECT_COUNT = 0

# ###################################################################################################################
# helper functions section
# ###################################################################################################################


def y(arg_v):
    if ratio > 2.1:
        return (INITIAL_DIMENSION * 2.5 / ratio) * (hy - arg_v) / (hy - yhy)
    else:
        return (INITIAL_DIMENSION / ratio) * (hy - arg_v) / (hy - yhy)


def x(arg_v):
    if ratio > 2.1:
        return INITIAL_DIMENSION * 2.5 * (arg_v - xwx) / (wx - xwx)
    else:
        return INITIAL_DIMENSION * (arg_v - xwx) / (wx - xwx)


# reset the line width to svg format
def getlinewidth(arg_l):
    if float(arg_l) != 1:
        return float(arg_l) * 3 + 1
    else:
        return str(format((float(arg_l) * 1.5), '.3f'))


# get text font size, 150 is the ratio
def gettextfontsize(arg_f):
    return arg_f * 150


def stroke(arg_c):
    if int(arg_c) != 134:
        stroke_string = "stroke=\"%s\""
        return stroke_string.replace('%s', color_list[int(arg_c)])
    else:
        return "stroke=\"#FFFFFF\""


def stroke_dash(arg_d):
    # print("dotted_or_dashed " + dotted_or_dashed[int(arg_d)])
    if arg_d in dotted_or_dashed:
        return " stroke-dasharray=" + dotted_or_dashed[int(arg_d)]
    else:
        return ""


def pline(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, argdnameval, arg_pd_g_line_count):
    global w, o
    if sec == 1:
        w = 0.02
    if (sec == 2) and (w > 0.02):
        w = 0.02
    if (sec == 1) and (dname.startswith('con_')):
        w = 0.03
    if (sec == 1) and (arg2 == 0):
        w = 0.03

    ls_g_id_line = SVG_G_LINE.replace('%s', str(arg_pd_g_line_count))
    ls_stroke = '<line %s'
    ls_lfmt = ls_stroke.replace('%s', stroke(int(arg2) - 1))
    ls_g_id_line = ls_g_id_line + ls_lfmt
    ls_stroke_dash = '%s'.replace('%s', stroke_dash(arg4))

    if stroke_dash(arg4) != '':
        ls_g_id_line = ls_g_id_line + ' ' + ls_stroke_dash

    ls_stroke_width = 'stroke-width=\"%s\"'.replace('%s', str(getlinewidth(arg3)))
    ls_g_id_line = ls_g_id_line + ' ' + ls_stroke_width
    ls_x1 = 'x1=\"%s\"'.replace('%s', str(format(x(float(arg5)), '.3f')))
    ls_y1 = 'y1=\"%s\"'.replace('%s', str(format(y(float(arg6)), '.3f')))
    ls_x2 = 'x2=\"%s\"'.replace('%s', str(format(x(float(arg7)), '.3f')))
    ls_y2 = 'y2=\"%s\"'.replace('%s', str(format(y(float(arg8)), '.3f')))
    ls_g_id_line = ls_g_id_line + ' ' + ls_x1 + ' ' + ls_x2 + ' ' + ls_y1 + ' ' + ls_y2
    ls_pb_line_ends = ''
    ls_g_id_line = ls_g_id_line + '' + ls_pb_line_ends
    ls_pb_line_style = ''
    ls_g_id_line = ls_g_id_line + '' + ls_pb_line_style
    ls_g_id_line = ls_g_id_line + '' + '></line>' + SVG_G_CLOSE

    return ls_g_id_line


def savedisplay():
    sys.stdout.write('%s' % ('          Entering SaveDisplay() ===>> ' + '\n'))
    sys.stdout.write('%s' % ('file ' + file + '\n'))
    # sys.stdout.write('%s' % ('filepath ' + filepath + '\n'))

    # This is where we will build the additional svg files for page based displays such as recloser control pages and accumulator pages, RTU pages, etc...
    # For Example: 5.2153.svg, 5.2153-1.svg & 5.2153-2.svg
    if previous_page_no > 0:
        fname_page = '-' + str(previous_page_no)
        dest = ''

    return 1


def prect(arg2, arg3, arg4, arg5, arg6, arg9, arg_pd_g_rect_count):
    # ########################################################
    # rectangle 7 18.108223 12.332685 0.400000 0.400000 1 0 3
    # 1         2 3         4         5        6        7 8 9
    # #######################################################
    global o

    rect_pts_str_x_of_3 = '{:8.4f}'.format(x(arg3)).lstrip(' ')
    rect_pts_str_y_of_4 = '{:8.4f}'.format(y(arg4)).lstrip(' ')
    rect_pts_str_x_of_3_plus_5 = '{:8.4f}'.format(x(arg3 + arg5)).lstrip(' ')
    rect_pts_str_y_of_4_minus_6 = '{:8.4f}'.format(y(arg4 - arg6)).lstrip(' ')

    rect_pts_str = rect_pts_str_x_of_3 + ',' + rect_pts_str_y_of_4 + ' ' + rect_pts_str_x_of_3_plus_5 + ',' + rect_pts_str_y_of_4 + ' ' + rect_pts_str_x_of_3_plus_5 + ',' + rect_pts_str_y_of_4_minus_6 + ' ' + rect_pts_str_x_of_3 + ',' + rect_pts_str_y_of_4_minus_6
    ls_temp_rect = SVG_POLYGON.replace('%s', str(arg_pd_g_rect_count), 1)
    ls_temp_rect_pts = ls_temp_rect.replace('points=\"%s\"', 'points=\"' + rect_pts_str + '\"')
    ls_temp_fill = ls_temp_rect_pts.replace('fill=\"%s\"', 'fill=\"' + 'none' + '\"')

    # For testing, make rectangles different colors from the clr array:
    # ls_temp_stroke = ls_temp_fill.replace('stroke=\"%s\"', 'stroke=\"' + clr[int(arg2) + int(arg_pd_g_rect_count)] + '\"')

    ls_temp_stroke = ls_temp_fill.replace('stroke=\"%s\"', 'stroke=\"' + color_list[int(arg2)] + '\"')

    if arg9 != 0:
        ls_temp_stroke_width = ls_temp_stroke.replace('stroke-width=\"%s\"', 'stroke-width=\"' + str(arg9) + '\"')
    else:
        ls_temp_stroke_width = ls_temp_stroke.replace('stroke-width=\"%s\"', 'stroke-width=\"' + '3' + '\"')

    return ls_temp_stroke_width


for subdir, dirs, files in os.walk(ROOTDIR):
    for file in files:
        filepath = subdir + os.sep + file
        image_table_count = 0
        sec = 0
        SVG_G_LINE_COUNT = 0
        SVG_G_RECT_COUNT = 0
        SVG_SVG_ANALOG_COUNTER = 0
        pline_return = ''
        prect_return = ''

        if filepath.endswith(".txt"):
            sys.stdout.write('%s' % ('filepath ' + filepath + '\n'))

            # ###########################################
            # MAIN TXT FILE PROCESSING LOOPING CONSTRUCT
            # ###########################################
            with open(filepath) as fp:
                for i, line in enumerate(fp):
                    if i in range(0, 500000, 1):
                        if VERBOSITY_LEVEL == 4:
                            sys.stdout.write('%s' % ('Line ' + str(i + 1) + '  ' + line))

                        if line.find('START') > -1:
                            START_count += 1
                            if VERBOSITY_LEVEL == 3:
                                sys.stdout.write('%s %s' % ('        START found in file ' + file + ' on line ' + str(i + 1) + ' this is occurrence No.: ' + str(START_count), '\n'))

                            if image_table_count > 0:
                                sec += 1
                                if VERBOSITY_LEVEL == 3:
                                    sys.stdout.write('%s %s' % ('        sec: ' + str(sec) + ' ========================================================================>>>> ', '\n'))

                        if line.find('image_table') > -1:
                            image_table_count += + 1
                            if VERBOSITY_LEVEL == 3:
                                sys.stdout.write('%s %s' % ('        image_table found in file ' + file + ' on line ' + str(i + 1) + ' this is occurrence No.: ' + str(image_table_count), '\n'))

                        # ##########################################################################################
                        # SECTION 2 CALCULATE RATIO
                        #   parse display type second start section and convert the view to larger width and height
                        # ##########################################################################################
                        if sec == 2:
                            results = re.findall(r"[-+]?\d*\.*\d+", line)
                            if results.__len__() == 4:
                                lower_left_x1_pos = float(results.__getitem__(0))
                                lower_left_y1_pos = float(results.__getitem__(1))
                                upper_right_x2_pos = float(results.__getitem__(2))
                                upper_right_y2_pos = float(results.__getitem__(3))
                                # sys.stdout.write('%s %.06f %.06f %.06f %.06f' % ('\n' + 'Ratio Operands: ', lower_left_x1_pos, lower_left_y1_pos, upper_right_x2_pos, upper_right_y2_pos) + '\n')
                                ratio = (upper_right_x2_pos - lower_left_x1_pos) / (upper_right_y2_pos - lower_left_y1_pos)
                                # sys.stdout.write('%s %.06f %s' % ('\nRatio: ', ratio, '\n'))
                                xwx = lower_left_x1_pos
                                yhy = lower_left_y1_pos
                                wx = upper_right_x2_pos
                                hy = upper_right_y2_pos

                                # sys.stdout.write('%s %s %s' % ('\nSVG_SVG_ROOT: ', SVG_SVG_ROOT, '\n'))
                                str_float = INITIAL_DIMENSION / ratio
                                str_string = str(round(str_float))
                                # sys.stdout.write('%s %s %s' % ('\nstr_string: ', str_string, '\n'))

                                # sys.stdout.write('%s %s %s' % ('\nSVG_SVG_ROOT: ', SVG_SVG_ROOT, '\n'))

                        # ###################################################
                        # SECTION 1 DEVICE SECTION
                        #     Load associative array (dict) with asi's/tsi's
                        # ###################################################
                        if (line.find('device') > -1) and (sec == 1):
                            device_count += 1
                            a, b = line.split(' ')
                            dname = re.sub('\|', '_', b)
                            dname = re.sub('\"', '', b)
                            if VERBOSITY_LEVEL == 3:
                                sys.stdout.write('%s' % ('        device ' + dname.rstrip() + ' found in sec ' + str(sec) + ' on line ' + str(i + 1) + ' Cnt: ' + str(device_count) + '\n'))

                                # ###############################################################################################################################################
                                # ASI Devices - section 1                       (asi displays for testing can be found 10.1010 - 10.1019)
                                # ###############################################################################################################################################
                                if (dname.startswith('asi')) and (sec == 1):
                                    if line.find('{') > -1:
                                        bracket_count += 1
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s' % '            bracket_count += 1 so count equals ' + str(bracket_count) + '\n')
                                    if line.find('}') > -1:
                                        bracket_count -= 1
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s' % '            bracket_count -= 1 so count equals ' + str(bracket_count) + '\n')

                                    if (bracket_count == 1) and (line.find('state') > -1):
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s' % '            asi, sec=1, brackets=1, state, bracket_count = ' + str(bracket_count) + '\n')

                                    if (bracket_count == 2) and (line.find('fill_arc') > -1):
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s' % '            asi, sec=1, brackets=2, fill_arc, bracket_count = ' + str(bracket_count) + '\n')
                                        asi_split_string = [str(i) for i in line.split(FS)]
                                        asir[dname] = asi_split_string.__getitem__(0)
                                        asirx[dname] = asi_split_string.__getitem__(3)
                                        asiry[dname] = asi_split_string.__getitem__(4)
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s %s %s' % ('asir[dname] ' + asir[dname], 'asirx[dname] ' + asirx[dname], 'asiry[dname] ' + asiry[dname] + '\n'))

                                    if (bracket_count == 2) and (line.find('line') > -1):
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s' % '            asi, sec=1, brackets=2, line, bracket_count = ' + str(bracket_count) + '\n')
                                        asi_split_string = [str(i) for i in line.split(FS)]
                                        asir[dname] = asi_split_string.__getitem__(0)
                                        asirx[dname] = asi_split_string.__getitem__(5)
                                        asiry[dname] = asi_split_string.__getitem__(6)
                                        asirxe[dname] = asi_split_string.__getitem__(7)
                                        asirye[dname] = asi_split_string.__getitem__(8)
                                        if VERBOSITY_LEVEL == 3:
                                            sys.stdout.write('%s %s %s %s %s' % ('asir[dname] ' + asir[dname], 'asirx[dname] ' + asirx[dname], 'asiry[dname] ' + asiry[dname], 'asirxe[dname] ' + asirxe[dname], 'asirye[dname] ' + asirye[dname] + '\n'))

                                            # ###############################################################################################################################################
                                            # TSI Devices - section 1
                                            # ###############################################################################################################################################
                                            if (dname.startswith('tsi')) and (sec == 1):
                                                if line.find('{') > -1:
                                                    bracket_count += 1
                                                    if VERBOSITY_LEVEL == 3:
                                                        sys.stdout.write('%s' % '            bracket_count += 1 so count equals ' + str(bracket_count) + '\n')
                                                if line.find('}') > -1:
                                                    bracket_count -= 1
                                                    if VERBOSITY_LEVEL == 3:
                                                        sys.stdout.write('%s' % '            bracket_count -= 1 so count equals ' + str(bracket_count) + '\n')

                                                # ###########################################################################################################################################
                                                # TSI states (0,1,2....)
                                                # ###########################################################################################################################################
                                                if (bracket_count == 1) and (line.find('state') > -1):
                                                    if VERBOSITY_LEVEL == 3:
                                                        sys.stdout.write('%s' % '            tsi, sec=1, brackets=1, state, bracket_count = ' + str(bracket_count) + '\n')

                                                    tsi_split_string = [str(i) for i in line.split(FS)]
                                                    tsi_state_number = tsi_split_string.__getitem__(1).rstrip('\n')

                                                if (bracket_count == 2) and (line.find('text') > -1):
                                                    if VERBOSITY_LEVEL == 3:
                                                        sys.stdout.write('%s' % '            tsi, sec=1, brackets=2, text, bracket_count = ' + str(bracket_count) + '\n')

                                                    tsi_split_string = [str(i) for i in line.split(FS)]
                                                    tsi_state[dname] = tsi_split_string.__getitem__(1)
                                                    tsi_x[dname] = tsi_split_string.__getitem__(2)
                                                    tsi_y[dname] = tsi_split_string.__getitem__(3)
                                                    tsi_off[dname] = tsi_split_string.__getitem__(4)
                                                    tsi_txt[dname] = tsi_split_string.__getitem__(5)
                                                    tsi_value[dname] = tsi_split_string.__getitem__(6).rstrip('\n')

                                                    # parse tsi text as multistate text, 2 duplicated state elemenets are created for transparency handling as work around
                                                    tsi_state[dname] = tsi_state_number + '|' + tsi_state[dname]
                                                    tsi_x[dname] = tsi_split_string.__getitem__(2) + '|' + tsi_x[dname]
                                                    tsi_y[dname] = tsi_split_string.__getitem__(3) + '|' + tsi_y[dname]
                                                    tsi_off[dname] = tsi_split_string.__getitem__(4) + '|' + tsi_off[dname]
                                                    tsi_txt[dname] = tsi_split_string.__getitem__(5) + '|' + tsi_txt[dname]
                                                    tsi_value[dname] = tsi_split_string.__getitem__(6).rstrip('\n') + '|' + tsi_value[dname].rstrip('\n')

                                                    if VERBOSITY_LEVEL == 3:
                                                        sys.stdout.write('%s %s %s %s %s %s %s' % ('                        state= ' + tsi_state[dname], ' x= ' + tsi_x[dname], ' y= ' + tsi_y[dname], ' offset= ' + tsi_off[dname], ' text= ' + tsi_txt[dname], ' value= ' + tsi_value[dname], '\n'))

                        # ####################
                        # CONTROL FLOW ROUTER
                        # ####################
                        if str(line).startswith('page'):
                            pageline_split_string = [str(i) for i in line.split(FS)]
                            page_no = int(pageline_split_string.__getitem__(1))
                            dstart = ''
                            dend = ''
                            # sys.stdout.write('%s' % 'page_no = ' + str(page_no) + ' previous_page_no = ' + str(previous_page_no) + '\n')
                            if page_no != previous_page_no:
                                savedisplay()
                                previous_page_no = page_no
                                o = ''
                                s = ''
                                ds = ''
                                tlqo = ''
                                ho = ''
                                ob = ''

                        # ##########################################################################################
                        # pline()
                        # ##########################################################################################
                        if str(line).lstrip('\t').startswith('line') and (sec == 2):
                            FS = ' '
                            sec_2_line_args_split_string = [str(i) for i in line.split(FS)]
                            num_of_sec_2_line_args = sec_2_line_args_split_string.__len__()
                            # print('num_of_sec_2_line_args: ', num_of_sec_2_line_args)

                            if num_of_sec_2_line_args == 10:
                                val0 = line
                                val1 = sec_2_line_args_split_string.__getitem__(0).lstrip('\t')
                                val2 = sec_2_line_args_split_string.__getitem__(1)
                                val3 = sec_2_line_args_split_string.__getitem__(2)
                                val4 = sec_2_line_args_split_string.__getitem__(3)
                                val5 = sec_2_line_args_split_string.__getitem__(4)
                                val6 = sec_2_line_args_split_string.__getitem__(5)
                                val7 = sec_2_line_args_split_string.__getitem__(6)
                                val8 = sec_2_line_args_split_string.__getitem__(7)
                                val9 = sec_2_line_args_split_string.__getitem__(8)

                                if dname.lstrip('\t').__len__() == 0:
                                    dnameval = 'no device'
                                    pline_return = pline(val0.lstrip('\t'), val1, val2, val3, val4, val5, val6, val7, val8, val9, dnameval, SVG_G_LINE_COUNT + 1)
                                else:
                                    pline_return = pline(val0.lstrip('\t'), val1, val2, val3, val4, val5, val6, val7, val8, val9, dname, SVG_G_LINE_COUNT + 1)
                                SVG_G_LINE_COUNT += 1
                                # pline_return = SVG_SVG_HEADER + "\n" + SVG_SVG_ROOT + "\n" + pline_return + "\n" + SVG_SVG_ROOT_CLOSE

                                if (SVG_G_LINE_COUNT == 1) and (SVG_G_RECT_COUNT == 0):
                                    sys.stdout.write('%s' % SVG_SVG_HEADER + "\n")
                                    sys.stdout.write('%s' % pline_return + "\n")
                                else:
                                    sys.stdout.write('%s' % pline_return + "\n")

                        # ##########################################################################################
                        # prect()
                        # ##########################################################################################
                        if str(line).lstrip('\t').startswith('rectangle') and (sec == 2):
                            FS = ' '
                            sec_2_rectsngle_args_split_string = [str(i) for i in line.split(FS)]
                            num_of_sec_2_rectangle_args = sec_2_rectsngle_args_split_string.__len__()
                            # print('num_of_sec_2_rectangle_args: ', num_of_sec_2_rectangle_args)

                            if num_of_sec_2_rectangle_args == 10:
                                val2 = float(sec_2_rectsngle_args_split_string.__getitem__(1)) - 1
                                val3 = float(sec_2_rectsngle_args_split_string.__getitem__(2))
                                val4 = float(sec_2_rectsngle_args_split_string.__getitem__(3))
                                val5 = float(sec_2_rectsngle_args_split_string.__getitem__(4))
                                val6 = float(sec_2_rectsngle_args_split_string.__getitem__(5))
                                val9 = float(sec_2_rectsngle_args_split_string.__getitem__(8))

                                prect_return = prect(val2, val3, val4, val5, val6, val9, SVG_G_RECT_COUNT + 1)
                                SVG_G_RECT_COUNT += 1
                                # prect_return = SVG_SVG_HEADER + "\n" + SVG_SVG_ROOT + "\n" + prect_return + "\n" + SVG_SVG_ROOT_CLOSE

                                if (SVG_G_RECT_COUNT == 1) and (SVG_G_LINE_COUNT == 0):
                                    sys.stdout.write('%s' % SVG_SVG_HEADER + "\n")
                                    sys.stdout.write('%s' % prect_return + "\n")
                                else:
                                    sys.stdout.write('%s' % prect_return + "\n")

            sys.stdout.write('%s' % SVG_SVG_HEADER_CLOSE + "\n")

            # Print out members of each element type (eg., lines, rectangles, etc.)
            # sys.stdout.write('%s' % 'pline_return = ' + pline_return)
            # sys.stdout.write('%s' % 'prect_return = ' + prect_return)

            fp.close()
            # break
# Turn on/off printing of all lines
# with open(filepath) as fp:
#     for i, line in enumerate(fp):
#         sys.stdout.write('%04d %s' % (i, ' ' + line))
# fp.close()

SVG_SVG_FILE_NAME = "Example.svg"
SVG_POLYGON_ROTATE = "<polygon id=\"polygon_%s_rotate\" points=\"%s\" fill=\"%s\" stroke=\"%s\" stroke-width=\"%s\" transform=\"%s\"></polygon>"
SVG_G_TEXT = "<g id=\"Text_%s\" %s stroke=\"none\" font-family=\"Times New Roman\" font-size=\"%.3f\">"
SVG_G_TEXT_RECT = "<rect id=\"Text%s_RET\" x=\"%s\" y=\"%s\" width=\"%s\" height=\"%s\" fill=\"none\" stroke-width=\"0\"></rect>"
SVG_G_TEXT_ACT = "<text id=\"Text%s_TXT\" x=\"%s\" y=\"%s\" %s stroke=\"none\" font-family=\"Times New Roman\" font-size=\"%s\">%s</text>"
SVG_G_TEXT_ACT_UNDER = "<text id=\"Text%s_TXT\" x=\"%s\" y=\"%s\" %s stroke=\"none\" font-family=\"Times New Roman\" font-size=\"%s\" text-decoration=\"underline\">%s</text>"
SVG_G_TEXT_BTN = "<a id=\"BTN_%s\" %s stroke=\"none\" font-family=\"Times New Roman\" font-size=\"%s\" pointer-events=\"all\" visibility=\"hidden\" xlink:show=\"new\" xlink:href=\"%s\" PB:ButtonAction=\".\\%s\" PB:ButtonRelativePath=\".\\%s\" PB:ButtonType=\"4\" PB:Type=\"9\" PB:Visible=\"False\" PB:Scripting=\"True\" PB:ButtonOptions=\"11\" PB:WorkingDirectory=\"\"><rect id=\"BTN_RECT_%s\" x=\"%s\" y=\"%s\" width=\"%s\" height=\"%s\" fill=\"\" stroke=\"%s\" stroke-with=\"%s\"></rect></a>"
SVG_G_TEXT_COUNT = 0
