"""
AutoCleaner.py

As version 1.852026, it only works with Shops Name available on LKA as of July 2026, further use of this application especially when working with IKA, requires updating 
the mapping in cleaning.py. Note that this is basically a name converter and grouping tool, not a full data cleaning tool. 
It is designed to be used in a simple workflow. YOU STILL NEED TO CHECK THE OUTPUT FILES MANUALLY FOR ERRORS AND INCONSISTENCIES.
if anything is wrong please try to understand the error code and try to fix it in cleaning.py, or should you require any assistance, 
please contact the developer (jayyidan1705@outlook.com).

This Application is strictly designed for internal use only, as it is highly specific to WMG's data and naming conventions.

HOW TO RUN IN TERMINAL (first time use)
1. pip install pandas openpyxl python-calamine
2. python AutoCleaner.py

Pick a file -> Run cleaning -> Save the result.

All actual cleaning logic lives in cleaning.py, this file is just the TKinter GUI.
"""