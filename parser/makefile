ANTLR = antlr4

all: compile 

compile: EventB.g4 B2Maude.py
		$(ANTLR) -Dlanguage=Python3 EventB.g4

clean:
		rm -f *.tokens *.interp
		rm -f  EventBLexer.py  EventBListener.py  EventBParser.py
