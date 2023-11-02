GEN = python ../greektrans.py

all:

regenerate:
	$(GEN) lords_prayer.txt > lords_prayer-romanized.txt
	$(GEN) -m lords_prayer.txt > lords_prayer-monotonized.txt
	$(GEN) inferno-1.txt > inferno-1-romanized.txt
	$(GEN) -m inferno-1.txt > inferno-1-monotonized.txt
