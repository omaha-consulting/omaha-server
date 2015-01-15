THEME="flatly-multi"
TARGET="README.md"
OUTPUT="index.html"

all:
	aglio -i $(TARGET) -o $(OUTPUT) -t $(THEME)

server:
	aglio -i $(TARGET) -s -t $(THEME)
