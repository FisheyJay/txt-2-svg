Name:   txt2svg.py
Author: John Fisher
Date:   10/24/2016     Initial Creation of production process. I am sharing this subset of logic as a learning example or                                        as a starting point for other developers having similar requirements.
Description:  Converts Ascii display export files (from various proprietary software applications) to Inline SVG. Functions for a                       particular file format but can be easily adapted to suit purposes for other Ascii text file formats such as AutoCAD *.DXF                 files. This process calculates a ratio and dynamically sizes and replicate lines, rectangles and polygons with the same                   aspect ratio, sizing and appearance as the source. I have stripped out all sensitive and proprietary information from this                 code and it's associated input data file.
Debugging:    Verbosity Level can be set as follows: 4 = Maximum, 3 = High, 2 = Medium, 1 = Low, 0 = None
              I have left some diagnostics in the form of sys.stdout.write() and print() statements in just the right spots that can be                 quickly uncommented to get visibility into something quickly. I personally prefer the PyCharm debugger, but if you are a                   newer developer, you will appreciate the simplicity. Plus I can be a little lazy and not cleanup the code so much. It is v                 very late and I am very tired, lol.
Input File:   Example.txt - Typically, you would process an AutoCAD DXF file which is very similar in format to this Example.txt file                   that's included herein.
Input File:   Please see File Format Definition which can be found in the Readme.md file in this same GitHub repository
Output FIle:  txt2svg.svg (see file in repo.)
Coming soon:  Functions to handle the replication of Text, Arcs, custom symbols, embedded real-time updating data points via hopefully an               open source xlink type data binding mechanism.
