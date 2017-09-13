
D:\迅雷下载\pycrypto-2.6.1\pycrypto-2.6.1>python setup.py install
running install
running build
running build_py
running build_ext
running build_configure
checking for gcc... gcc
checking whether the C compiler works... yes
checking for C compiler default output file name... a.exe
checking for suffix of executables... .exe
checking whether we are cross compiling... no
checking for suffix of object files... o
checking whether we are using the GNU C compiler... yes
checking whether gcc accepts -g... yes
checking for gcc option to accept ISO C89... none needed
checking for __gmpz_init in -lgmp... no
checking for __gmpz_init in -lmpir... no
checking whether mpz_powm is declared... no
checking whether mpz_powm_sec is declared... no
checking how to run the C preprocessor... gcc -E
checking for grep that handles long lines and -e... /usr/bin/grep
checking for egrep... /usr/bin/grep -E
checking for ANSI C header files... yes
checking for sys/types.h... yes
checking for sys/stat.h... yes
checking for stdlib.h... yes
checking for string.h... yes
checking for memory.h... yes
checking for strings.h... yes
checking for inttypes.h... yes
checking for stdint.h... yes
checking for unistd.h... yes
checking for inttypes.h... (cached) yes
checking limits.h usability... yes
checking limits.h presence... yes
checking for limits.h... yes
checking stddef.h usability... yes
checking stddef.h presence... yes
checking for stddef.h... yes
checking for stdint.h... (cached) yes
checking for stdlib.h... (cached) yes
checking for string.h... (cached) yes
checking wchar.h usability... yes
checking wchar.h presence... yes
checking for wchar.h... yes
checking for inline... inline
checking for int16_t... yes
checking for int32_t... yes
checking for int64_t... yes
checking for int8_t... yes
checking for size_t... yes
checking for uint16_t... yes
checking for uint32_t... yes
checking for uint64_t... yes
checking for uint8_t... yes
checking for stdlib.h... (cached) yes
checking for GNU libc compatible malloc... yes
checking for memmove... yes
checking for memset... yes
configure: creating ./config.status
config.status: creating src/config.h
warning: GMP or MPIR library not found; Not building Crypto.PublicKey._fastmath.

building 'Crypto.Random.OSRNG.winrandom' extension
creating build\temp.win-amd64-2.7
creating build\temp.win-amd64-2.7\Release
creating build\temp.win-amd64-2.7\Release\src
C:\MinGW\bin\gcc.exe -mdll -Wall -std=c99 -O3 -fomit-frame-pointer -Isrc/ -IC:\P
ython27\include -IC:\Python27\PC -c src/winrand.c -o build\temp.win-amd64-2.7\Re
lease\src\winrand.o
src/winrand.c:38:0: warning: "_WIN32_WINNT" redefined
 #define _WIN32_WINNT 0x400
 ^
In file included from c:\mingw\include\w32api.h:59:0,
                 from c:\mingw\include\_mingw.h:73,
                 from c:\mingw\include\io.h:51,
                 from C:\Python27\include/pyconfig.h:68,
                 from C:\Python27\include/Python.h:8,
                 from src/winrand.c:33:
c:\mingw\include\sdkddkver.h:184:0: note: this is the location of the previous d
efinition
 #  define _WIN32_WINNT _WIN32_WINNT_WIN2K
 ^
writing build\temp.win-amd64-2.7\Release\src\winrandom.def
C:\MinGW\bin\gcc.exe -shared -s build\temp.win-amd64-2.7\Release\src\winrand.o b
uild\temp.win-amd64-2.7\Release\src\winrandom.def -LC:\Python27\libs -LC:\Python
27\PCbuild\amd64 -lws2_32 -ladvapi32 -lpython27 -lmsvcr90 -o build\lib.win-amd64
-2.7\Crypto\Random\OSRNG\winrandom.pyd
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x4c): undefined
 reference to `_imp__PyArg_ParseTupleAndKeywords'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x92): undefined
 reference to `_imp___PyObject_New'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0xbb): undefined
 reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0xd6): undefined
 reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x140): undefine
d reference to `_imp__PyArg_ParseTuple'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x168): undefine
d reference to `_imp__PyMem_Malloc'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1b9): undefine
d reference to `_imp__PyString_FromStringAndSize'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1c4): undefine
d reference to `_imp__PyMem_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1d6): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1e9): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x20a): undefine
d reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x21d): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x226): undefine
d reference to `_imp__PyMem_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x236): undefine
d reference to `_imp__PyErr_NoMemory'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x241): undefine
d reference to `_imp__PyExc_ValueError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x254): undefine
d reference to `_imp__PyErr_SetString'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x298): undefine
d reference to `_imp__Py_FindMethod'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2b2): undefine
d reference to `_imp__PyInt_FromLong'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2c1): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2d4): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x302): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x315): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x34b): undefine
d reference to `_imp__PyObject_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x35a): undefine
d reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x36d): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x386): undefine
d reference to `_imp__PyType_Type'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x3b8): undefine
d reference to `_imp__Py_InitModule4'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x3c0): undefine
d reference to `_imp__PyModule_AddIntConstant'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x4ec): undefine
d reference to `_imp__PyModule_AddStringConstant'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x585): undefine
d reference to `_imp__PyErr_Occurred'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x596): undefine
d reference to `_imp__Py_FatalError'
collect2.exe: error: ld returned 1 exit status
error: command 'C:\\MinGW\\bin\\gcc.exe' failed with exit status 1

D:\迅雷下载\pycrypto-2.6.1\pycrypto-2.6.1>python setup.py build
running build
running build_py
running build_ext
running build_configure
warning: GMP or MPIR library not found; Not building Crypto.PublicKey._fastmath.

building 'Crypto.Random.OSRNG.winrandom' extension
C:\MinGW\bin\gcc.exe -mdll -Wall -std=c99 -O3 -fomit-frame-pointer -Isrc/ -IC:\P
ython27\include -IC:\Python27\PC -c src/winrand.c -o build\temp.win-amd64-2.7\Re
lease\src\winrand.o
src/winrand.c:38:0: warning: "_WIN32_WINNT" redefined
 #define _WIN32_WINNT 0x400
 ^
In file included from c:\mingw\include\w32api.h:59:0,
                 from c:\mingw\include\_mingw.h:73,
                 from c:\mingw\include\io.h:51,
                 from C:\Python27\include/pyconfig.h:68,
                 from C:\Python27\include/Python.h:8,
                 from src/winrand.c:33:
c:\mingw\include\sdkddkver.h:184:0: note: this is the location of the previous d
efinition
 #  define _WIN32_WINNT _WIN32_WINNT_WIN2K
 ^
writing build\temp.win-amd64-2.7\Release\src\winrandom.def
C:\MinGW\bin\gcc.exe -shared -s build\temp.win-amd64-2.7\Release\src\winrand.o b
uild\temp.win-amd64-2.7\Release\src\winrandom.def -LC:\Python27\libs -LC:\Python
27\PCbuild\amd64 -lws2_32 -ladvapi32 -lpython27 -lmsvcr90 -o build\lib.win-amd64
-2.7\Crypto\Random\OSRNG\winrandom.pyd
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x4c): undefined
 reference to `_imp__PyArg_ParseTupleAndKeywords'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x92): undefined
 reference to `_imp___PyObject_New'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0xbb): undefined
 reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0xd6): undefined
 reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x140): undefine
d reference to `_imp__PyArg_ParseTuple'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x168): undefine
d reference to `_imp__PyMem_Malloc'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1b9): undefine
d reference to `_imp__PyString_FromStringAndSize'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1c4): undefine
d reference to `_imp__PyMem_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1d6): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x1e9): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x20a): undefine
d reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x21d): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x226): undefine
d reference to `_imp__PyMem_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x236): undefine
d reference to `_imp__PyErr_NoMemory'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x241): undefine
d reference to `_imp__PyExc_ValueError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x254): undefine
d reference to `_imp__PyErr_SetString'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x298): undefine
d reference to `_imp__Py_FindMethod'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2b2): undefine
d reference to `_imp__PyInt_FromLong'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2c1): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x2d4): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x302): undefine
d reference to `_imp__PyExc_TypeError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x315): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x34b): undefine
d reference to `_imp__PyObject_Free'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x35a): undefine
d reference to `_imp__PyExc_SystemError'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x36d): undefine
d reference to `_imp__PyErr_Format'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x386): undefine
d reference to `_imp__PyType_Type'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x3b8): undefine
d reference to `_imp__Py_InitModule4'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x3c0): undefine
d reference to `_imp__PyModule_AddIntConstant'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x4ec): undefine
d reference to `_imp__PyModule_AddStringConstant'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x585): undefine
d reference to `_imp__PyErr_Occurred'
build\temp.win-amd64-2.7\Release\src\winrand.o:winrand.c:(.text+0x596): undefine
d reference to `_imp__Py_FatalError'
collect2.exe: error: ld returned 1 exit status
error: command 'C:\\MinGW\\bin\\gcc.exe' failed with exit status 1

D:\迅雷下载\pycrypto-2.6.1\pycrypto-2.6.1>