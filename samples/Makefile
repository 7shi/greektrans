GEN1 = python ../greektrans.py
GEN2 = deno run --allow-read ../greektrans.js

all:

regenerate:
	$(GEN1) lords_prayer.txt > lords_prayer-romanized.txt
	$(GEN1) -m lords_prayer.txt > lords_prayer-monotonized.txt
	$(GEN1) inferno-1.txt > inferno-1-romanized.txt
	$(GEN1) -m inferno-1.txt > inferno-1-monotonized.txt

test:
	$(GEN2) lords_prayer.txt > test-lords_prayer-romanized.txt
	$(GEN2) -m lords_prayer.txt > test-lords_prayer-monotonized.txt
	$(GEN2) inferno-1.txt > test-inferno-1-romanized.txt
	$(GEN2) -m inferno-1.txt > test-inferno-1-monotonized.txt
	diff -u lords_prayer-romanized.txt test-lords_prayer-romanized.txt
	diff -u lords_prayer-monotonized.txt test-lords_prayer-monotonized.txt
	diff -u inferno-1-romanized.txt test-inferno-1-romanized.txt
	diff -u inferno-1-monotonized.txt test-inferno-1-monotonized.txt

clean:
	rm -f test-*
