THEME="triple"
TARGET="README.md"
OUTPUT="index.html"

all:
	aglio -i $(TARGET) -o $(OUTPUT) --theme-template $(THEME)

server:
	aglio -i $(TARGET) -s --theme-template $(THEME) --host 0.0.0.0
