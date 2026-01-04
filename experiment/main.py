"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Main script to run the Episodic Extinction experiment.
"""

# import argparse
# import os
# from datetime import datetime
# from session import ExtinctionSession


# def main():
#     """Main function to run the experiment."""
#     parser = argparse.ArgumentParser(
#         description='Run the Episodic Extinction experiment'
#     )
    
#     parser.add_argument(
#         '--subject',
#         type=str,
#         default='test',
#         help='Subject ID (default: test)'
#     )
    
#     parser.add_argument(
#         '--session',
#         type=int,
#         default=1,
#         help='Session number (default: 1)'
#     )
    
#     parser.add_argument(
#         '--run',
#         type=int,
#         default=1,
#         help='Run number (default: 1)'
#     )
    
#     parser.add_argument(
#         '--output-dir',
#         type=str,
#         default='data',
#         help='Output directory for data files (default: data)'
#     )
    
#     parser.add_argument(
#         '--settings',
#         type=str,
#         default=None,
#         help='Path to settings file (optional)'
#     )
    
#     args = parser.parse_args()
    
#     # Create output directory if it doesn't exist
#     if not os.path.exists(args.output_dir):
#         os.makedirs(args.output_dir)
    
#     # Create output string with timestamp
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     output_str = f'sub-{args.subject}_ses-{args.session}_run-{args.run}_{timestamp}'
    
#     print(f"Starting Episodic Extinction Experiment")
#     print(f"Subject: {args.subject}")
#     print(f"Session: {args.session}")
#     print(f"Run: {args.run}")
#     print(f"Output: {os.path.join(args.output_dir, output_str)}")
#     print("-" * 50)
    
#     # Create and run session
#     try:
#         session = ExtinctionSession(
#             output_str=output_str,
#             output_dir=args.output_dir,
#             settings_file=args.settings
#         )
        
#         session.run()
        
#         print("\nExperiment completed successfully!")
        
#     except ImportError as e:
#         print(f"\nImport error: {e}")
#         print("Make sure exptools2 is installed: pip install -r requirements.txt")
#         raise
#     except KeyboardInterrupt:
#         print("\nExperiment interrupted by user.")
#         raise
#     except Exception as e:
#         print(f"\nError running experiment: {e}")
#         raise
    
#     finally:
#         print("Experiment ended.")


# if __name__ == '__main__':
#     main()

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
    
    output_str= subject+'_'+sess+'_'
    
    output_dir = './logs/'+output_str+'_Logs'
    
    if os.path.exists(output_dir):
        print("Warning: output directory already exists. Renaming to avoid overwriting.")
        output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')
    
    settings_file='./expsettings.yml'

    ts = ExtinctionSession(output_str=output_str, output_dir=output_dir, settings_file=settings_file)
    ts.run()

if __name__ == '__main__':
    main()
