PYTHON = python3
TESTS  = ./examples/B-book-models/ch2-cars-bridge.maude \
		 ./examples/B-book-models/ch2-cars-bridge2.maude \
		 ./examples/B-book-models/ch3-mechanical-press.maude \
		 ./examples/B-book-models/ch3-mechanical-press2.maude \
		 ./examples/B-book-models/ch4-file2.maude \
		 ./examples/B-book-models/ch4-file3.maude \
		 ./examples/B-book-models/ch4-file.maude \
		 ./examples/B-book-models/ch7-reader-writer.maude \
		 ./examples/bounded-retransmission-protocol/b-retrans-4.maude \
		 ./examples/bounded-retransmission-protocol/b-retrans-5-no-retry.maude \
		 ./examples/bounded-retransmission-protocol/b-retrans-5.maude \
		 ./examples/consensus-PNL/PNL1.maude \
		 ./examples/consensus-PNL/PNL2.maude \
		 ./examples/consensus-PNL/PNL3.maude \
		 ./examples/mechanical-systems/brake-system.maude \
		 ./examples/mechanical-systems/gear-system.maude \
		 ./examples/p2p-protocol/p2p-protocol.maude

all: compile $(TESTS)

compile: 
		$(MAKE) -C ./parser compile

%.maude: %.b ./parser/B2Maude.py
	$(PYTHON) ./parser/B2Maude.py --input $<  --output $@ 

clean:
		rm -vf $(TESTS)
		$(MAKE) -C ./parser clean
		
