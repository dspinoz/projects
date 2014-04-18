SUBDIRS = common

bin_PROGRAMS = hello
hello_SOURCES = main.c
hello_CPPFLAGS = -Icommon
hello_LDADD = common/libcommon.a

check_SCRIPTS = greptest.sh
TESTS = $(check_SCRIPTS)

greptest.sh:
	echo './hello | grep -i "hello"' > greptest.sh
	chmod +x greptest.sh

CLEANFILES = greptest.sh
