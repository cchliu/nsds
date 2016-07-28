"""
	Helper functions
"""
import os

def create_dir(indir):
	if not os.path.exists(indir):
		os.makedirs(indir)

	
