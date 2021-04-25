PREFIX := ~/.local
BIN_DIR := bin
LIB_DIR := lib/python3.9/site-packages
BIN_PATH := $(PREFIX)/$(BIN_DIR)
LIB_PATH := $(PREFIX)/$(LIB_DIR)
BIN_SOURCES := $(wildcard *.py)
LIB_SOURCES := generate_header_compile_commands.py
BIN_TARGETS := $(patsubst %.py,$(BIN_PATH)/%,$(BIN_SOURCES))
LIB_TARGETS := $(patsubst %.py,$(LIB_PATH)/%.py,$(LIB_SOURCES))

$(BIN_PATH)/%: %.py
	install $< $@

$(LIB_PATH)/%.py: %.py
	install $< $@

install: $(BIN_TARGETS) $(LIB_TARGETS)

uninstall:
	rm -f $(BIN_TARGETS) $(LIB_TARGETS)
