# DBC Code Generator

## Overview
This repo contains two scripts that will take a CAN DBC file and generate a header file for ether C or C++ code. The C version creates structs for each message with the correct type. The C++ version creates a class for each message.

## Dependencies
The scripts are written in Python 2.7 (untested on 3.6).

Run: 

    pip install -r requirements.txt
To get the needed python packages.

## How to Use
To generate the C or C++ header file, just run the scripts with a DBC and a specified output file.

C header:

    python dbc_to_h.py example.dbc -o can_messages.h

C++ header:

    python dbc_to_hpp.py example.dbc -o can_messages.hpp


See example.cpp on how to use the headers

## Know Issues
* Scripts can't handle CAN signals that aren't multiples of 8 bits (integer number of bytes).
* Need to add cycle time and scale fileds from signals.

## Changelog
21 Jan 2018 - 0.0.1 - Initial Release