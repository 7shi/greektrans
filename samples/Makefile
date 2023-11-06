GEN1 = python ../greektrans.py
GEN2 = deno run --allow-read ../greektrans.js

SAMPLES = lords_prayer inferno-1 inferno-2

all:

regenerate:
	for s in $(SAMPLES); do \
		$(GEN1)    $$s.txt > $$s-romanized.txt; \
		$(GEN1) -m $$s.txt > $$s-monotonized.txt; \
	done

test:
	for s in $(SAMPLES); do \
		$(GEN2)    $$s.txt > test-$$s-romanized.txt; \
		$(GEN2) -m $$s.txt > test-$$s-monotonized.txt; \
		diff -u $$s-romanized.txt   test-$$s-romanized.txt; \
		diff -u $$s-monotonized.txt test-$$s-monotonized.txt; \
	done

clean:
	rm -f test-*
