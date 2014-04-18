

AC_INIT([Hello World], [1.0])
AM_INIT_AUTOMAKE

AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_RANLIB
AM_PROG_CC_C_O

AC_CONFIG_SRCDIR([src/main.c])
AC_CONFIG_HEADERS([config.h])

AC_CHECK_HEADERS([stdio.h])

AC_CONFIG_FILES([Makefile
                 src/common/Makefile
                 src/Makefile
                 ])

AC_OUTPUT
echo \
"-------------------------------------------------

 ${PACKAGE_NAME} Version ${PACKAGE_VERSION}

 Prefix: '${prefix}'.
 Compiler: '${CC} ${CFLAGS} ${CPPFLAGS}'
 Libraries: '${LIBS}'

 Package features:
    None (yet)

 Now type 'make @<:@<target>@:>@'
   where the optional <target> is:
     all                - build all binaries
     install            - install everything
     check              - run unit tests
     dist               - build distribution tarball
     distcheck          - build, run tests and generate distribution tar

--------------------------------------------------"
