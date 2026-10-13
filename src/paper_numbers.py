"""Compatibility entry point for the complete corrected numerical analysis."""
try:from .analyse import main
except ImportError:from analyse import main
if __name__=='__main__':main()
