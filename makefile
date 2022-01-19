PYTHON = python3
TESTS  = ./examples/brake-system.maude \
		 ./examples/gear-system.maude \
		 ./examples/p2p-protocol.maude

all: compile $(TESTS)

compile: 
		$(MAKE) -C ./parser compile

%.maude: %.b ./parser/B2Maude.py
	$(PYTHON) ./parser/B2Maude.py --input $<  --output $@ 

clean:
		rm -vf $(TESTS)
		$(MAKE) -C ./parser clean
		
