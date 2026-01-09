"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Main script to run the Episodic Extinction experiment.
"""

import sys
import os
from session import ExtinctionSession
from datetime import datetime
datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    subject = sys.argv[1]
    sess =  sys.argv[2]
    # version = sys.argv[3]
    # eyetracker_on = bool(sys.argv[4])
    
    output_str= subject+'_'+sess
    
    output_dir = f'./logs/sub-{subject}/{output_str}_Logs'
    
    if os.path.exists(output_dir):
        print("Warning: output directory already exists. Renaming to avoid overwriting.")
        output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')
    
    settings_file='./expsettings.yml'

    ts = ExtinctionSession(
        output_str=output_str, 
        output_dir=output_dir, 
        settings_file=settings_file,
        sess=int(sess)
        )
    ts.run()

if __name__ == '__main__':
    main()
