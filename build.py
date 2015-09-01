#!/usr/bin/env python
#---------------------------------------------------------------------
# IDAPython - Python plugin for Interactive Disassembler
#
# (c) The IDAPython Team <idapython@googlegroups.com>
#
# All rights reserved.
#
# For detailed copyright information see the file COPYING in
# the root of the distribution archive.
#---------------------------------------------------------------------
# build.py - Custom build script
#---------------------------------------------------------------------
import os
import platform
import shutil
import sys
import types
import zipfile
import glob
from distutils import sysconfig

from argparse import ArgumentParser, RawTextHelpFormatter

# Start of user configurable options
IDA_MAJOR_VERSION = 6
IDA_MINOR_VERSION = 8

IDA_SDK = ""
if 'IDA' in os.environ:
    IDA_SDK = os.environ['IDA']
else:
    candidate = os.path.join("..", "..", "include")
    if os.path.exists(candidate):
        IDA_SDK = candidate

parser = ArgumentParser(epilog="""
Since a very specific version of SWiG is expected in order to produce reliable
bindings, and if your platform doesn't provide that version by default and you
had to build/install it yourself, you will have to specify '--swig-bin' and
'--swig-inc' arguments.

For example, this is how to build against IDA 6.8 on linux, with a SWiG 2.0.12
installation located in /opt/my-swig/:

python build.py --ida-sdk /path/to/idasdk68/ \\
    --swig-bin /opt/my-swig/bin/swig \\
    --swig-inc /opt/my-swig/share/swig/2.0.12/python/:/opt/my-swig/share/swig/2.0.12

Notes:
 * '--swig-inc' here has 2 path components, separated by the platform's
   path separator; i.e., ':' in this case (if you were building on Windows,
   you would have to use ';'.)
 * SWiG can be tricky to deal with when specifying input paths. The path
   to the '.../2.0.12/python/' subdirectory should be placed before the
   more global '.../2.0.12/' directory.
""",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument("--ida-sdk", type=str, help="Path to the IDA SDK", default=IDA_SDK)
parser.add_argument("--swig-bin", type=str, help="Path to the SWIG binary", default="")
parser.add_argument("--swig-inc", type=str, help="Path(s) to the SWIG includes directory(ies)", default="")
parser.add_argument("--with-hexrays", help="Build Hex-Rays decompiler bindings (requires the 'hexrays.hpp' header to be present in the SDK's include/ directory)", default=False, action="store_true")
parser.add_argument("--ea64", help="Build 64-bit EA version of the plugin", default=False, action="store_true")
parser.add_argument("--debug", help="Build debug version of the plugin", default=False, action="store_true")
parser.add_argument("-v", "--verbose", help="Verbose mode", default=False, action="store_true")
args = parser.parse_args()

IDA_SDK = args.ida_sdk
assert os.path.exists(IDA_SDK), "Could not find IDA SDK include path (looked in: \"%s\")" % IDA_SDK

SWIG_BIN = args.swig_bin or "swig"
SWIG_INC = []
if args.swig_inc:
    SWIG_INC = map(lambda p: "-I%s" % p, args.swig_inc.split(os.pathsep))

# End of user configurable options

# IDAPython version
VERSION_MAJOR  = 1
VERSION_MINOR  = 7
VERSION_PATCH  = 2

# Determine Python version
PYTHON_MAJOR_VERSION = int(platform.python_version()[0])
PYTHON_MINOR_VERSION = int(platform.python_version()[2])

# Find Python headers
PYTHON_INCLUDE_DIRECTORY = sysconfig.get_config_var('INCLUDEPY')

# Swig command-line parameters
SWIG_OPTIONS = ['-modern', '-python', '-threads', '-c++', '-w451', '-shadow', '-D__GNUC__']
SWIG_OPTIONS.extend(SWIG_INC)

# Common macros for all compilations
COMMON_MACROS = [
    ("VER_MAJOR",  "%d" % VERSION_MAJOR),
    ("VER_MINOR",  "%d" % VERSION_MINOR),
    ("VER_PATCH",  "%d" % VERSION_PATCH),
    "__IDP__",
    ("MAXSTR", "1024"),
    "USE_DANGEROUS_FUNCTIONS",
    "USE_STANDARD_FILE_FUNCTIONS" ]

# Common includes for all compilations
COMMON_INCLUDES = [ ".", "swig" ]

# -----------------------------------------------------------------------
# List files for the binary distribution
BINDIST_MANIFEST = [
    "README.md",
    "COPYING.txt",
    "CHANGES.txt",
    "AUTHORS.txt",
    "STATUS.txt",
    "python.cfg",
    "docs/notes.txt",
    "examples/chooser.py",
    "examples/colours.py",
    "examples/ex_idphook_asm.py",
    "examples/ex_uirequests.py",
    "examples/debughook.py",
    "examples/ex_cli.py",
    "examples/ex1.idc",
    "examples/ex_custdata.py",
    "examples/ex1_idaapi.py",
    "examples/ex1_idautils.py",
    "examples/hotkey.py",
    "examples/structure.py",
    "examples/ex_gdl_qflow_chart.py",
    "examples/ex_strings.py",
    "examples/ex_actions.py",
    "examples/ex_func_chooser.py",
    "examples/ex_choose2.py",
    "examples/ex_debug_names.py",
    "examples/ex_graph.py",
    "examples/ex_hotkey.py",
    "examples/ex_patch.py",
    "examples/ex_expr.py",
    "examples/ex_timer.py",
    "examples/ex_dbg.py",
    "examples/ex_custview.py",
    "examples/ex_prefix_plugin.py",
    "examples/ex_pyside.py",
    "examples/ex_pyqt.py",
    "examples/ex_askusingform.py",
    "examples/ex_uihook.py",
    "examples/ex_idphook_asm.py",
    "examples/ex_imports.py"
]

# -----------------------------------------------------------------------
# List files for the source distribution (appended to binary list)
SRCDIST_MANIFEST = [
    "BUILDING.txt",
    "python.cpp",
    "basetsd.h",
    "build.py",
    "python.cfg",
    "swig/allins.i",
    "swig/area.i",
    "swig/auto.i",
    "swig/bytes.i",
    "swig/dbg.i",
    "swig/diskio.i",
    "swig/entry.i",
    "swig/enum.i",
    "swig/expr.i",
    "swig/fixup.i",
    "swig/frame.i",
    "swig/funcs.i",
    "swig/gdl.i",
    "swig/ida.i",
    "swig/idaapi.i",
    "swig/idd.i",
    "swig/idp.i",
    "swig/ints.i",
    "swig/kernwin.i",
    "swig/lines.i",
    "swig/loader.i",
    "swig/moves.i",
    "swig/nalt.i",
    "swig/name.i",
    "swig/netnode.i",
    "swig/offset.i",
    "swig/pro.i",
    "swig/queue.i",
    "swig/search.i",
    "swig/segment.i",
    "swig/srarea.i",
    "swig/strlist.i",
    "swig/struct.i",
    "swig/typeconv.i",
    "swig/typeinf.i",
    "swig/ua.i",
    "swig/xref.i",
    "swig/graph.i",
    "swig/fpro.i",
    "swig/hexrays.i",
]

def run(proc_argv):
    import subprocess
    if args.verbose:
        print "Running subprocess with argv: %s" % proc_argv
    subprocess.check_call(proc_argv)
    return 0

# -----------------------------------------------------------------------
class BuilderBase:
    """ Base class for builders """
    def __init__(self):
        pass


    def compile(self, source, objectname=None, includes=[], macros=[]):
        """
        Compile the source file
        """
        allmacros = []
        allmacros.extend(COMMON_MACROS)
        allmacros.extend(self.basemacros)
        allmacros.extend(macros)
        defines_argv = self._build_command_string(allmacros, self.define_directive)

        allincludes = []
        allincludes.extend(COMMON_INCLUDES)
        allincludes.extend(includes)
        includes_argv = self._build_command_string(allincludes, self.include_directive)

        if not objectname:
            objectname = source + self.object_extension

        argv = [self.compiler]
        argv.extend(self.compiler_parameters)
        argv.extend(self.compiler_out_string(objectname))
        argv.extend(self.compiler_in_string(source + self.source_extension))
        argv.extend(includes_argv)
        argv.extend(defines_argv)
        return run(argv)


    def link(self, objects, outfile, libpaths=[], libraries=[], extra_parameters=None):
        """ Link the binary from objects and libraries """

        argv = [self.linker]
        argv.extend(self.linker_parameters)
        argv.extend(self.linker_out_string(outfile))
        argv.extend(map(lambda o: o + self.object_extension, objects))
        argv.extend(map(lambda l: "%s%s" % (self.libpath_directive, l), libpaths))
        argv.extend(libraries)
        argv.extend(extra_parameters)
        return run(argv)


    def _build_command_string(self, tokens, directive):
        out = []
        for token in tokens:
            if type(token) == types.TupleType:
                out.append('%s%s=%s' % (directive, token[0], token[1]))
            else:
                out.append('%s%s' % (directive, token))
        return out


# -----------------------------------------------------------------------
class GCCBuilder(BuilderBase):
    """ Generic GCC compiler class """
    def __init__(self):
        self.include_directive = "-I"
        self.define_directive = "-D"
        self.libpath_directive = "-L"
        self.compiler_parameters = ["-m32", "-fpermissive", "-Wno-write-strings"]
        self.linker_parameters = ["-m32", "-shared"]
        self.basemacros = [ ]
        self.compiler = "g++"
        self.linker = "g++"
        self.source_extension = ".cpp"
        self.object_extension = ".o"

    def compiler_in_string(self, filename):
        return ["-c", filename]

    def compiler_out_string(self, filename):
        return ["-o", filename]

    def linker_out_string(self, filename):
        return ["-o", filename]


# -----------------------------------------------------------------------
class MSVCBuilder(BuilderBase):
    """ Generic Visual C compiler class """
    def __init__(self):
        self.include_directive = "/I"
        self.define_directive = "/D"
        self.libpath_directive = "/LIBPATH:"
        self.compiler_parameters = ["/nologo", "/EHsc"]
        self.linker_parameters = ["/nologo", "/dll", "/export:PLUGIN"]
        self.basemacros = [ "WIN32",
                            "_USRDLL",
                            "__NT__" ]
        self.compiler = "cl"
        self.linker = "link"
        self.source_extension = ".cpp"
        self.object_extension = ".obj"

    def compiler_in_string(self, filename):
        return ["/c", filename]

    def compiler_out_string(self, filename):
        return ["/Fo%s" % filename]

    def linker_out_string(self, filename):
        return ["/out:%s" % filename]

# -----------------------------------------------------------------------
def build_distribution(manifest, distrootdir, ea64, nukeold):
    """ Create a distibution to a directory and a ZIP file """
    # (Re)create the output directory
    if args.verbose:
        print "Distribution is in: %s" % distrootdir
    if nukeold and os.path.exists(distrootdir):
        shutil.rmtree(distrootdir)
    if not os.path.exists(distrootdir):
        os.makedirs(distrootdir)

    # Also make a ZIP archive of the build
    zippath = distrootdir + ".zip"
    zip = zipfile.ZipFile(zippath, nukeold and "w" or "a", zipfile.ZIP_DEFLATED)

    # Copy files, one by one
    for f in manifest:
        if type(f) == types.TupleType:
            srcfilepath = f[0]
            srcfilename = os.path.basename(srcfilepath)
            dstdir = os.path.join(distrootdir, f[1])
            dstfilepath = os.path.join(dstdir, srcfilename)
        else:
            srcfilepath = f
            srcfilename = os.path.basename(f)
            srcdir  = os.path.dirname(f)
            if srcdir == "":
                dstdir = distrootdir
            else:
                dstdir = os.path.join(distrootdir, srcdir)

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        dstfilepath = os.path.join(dstdir, srcfilename)
        shutil.copyfile(srcfilepath, dstfilepath)
        zip.write(dstfilepath)

    zip.close()


# -----------------------------------------------------------------------
def build_plugin(
        platform,
        idasdkdir,
        plugin_name,
        ea64):
    """ Build the plugin from the SWIG wrapper and plugin main source """

    global SWIG_OPTIONS

    # Get the arguments
    with_hexrays = args.with_hexrays

    # Path to the IDA SDK headers
    ida_include_directory = os.path.join(idasdkdir, "include")

    builder = None
    # Platform-specific settings for the Linux build
    if platform == "linux":
        builder = GCCBuilder()
        platform_macros = [ "__LINUX__" ]
        python_libpath = os.path.join(sysconfig.EXEC_PREFIX, "lib")
        python_library = ["-Bdynamic", "-lpython%d.%d" % (PYTHON_MAJOR_VERSION, PYTHON_MINOR_VERSION)]
        ida_libpath = os.path.join(idasdkdir, "lib", ea64 and "x86_linux_gcc_64" or "x86_linux_gcc_32")
        ida_lib = ""
        extra_link_parameters = ["-s"]
        builder.compiler_parameters.append("-O2")
    # Platform-specific settings for the Windows build
    elif platform == "win32":
        builder = MSVCBuilder()
        platform_macros = [ "__NT__" ]
        python_libpath = os.path.join(sysconfig.EXEC_PREFIX, "libs")
        python_library = ["python%d%d.lib" % (PYTHON_MAJOR_VERSION, PYTHON_MINOR_VERSION)]
        ida_libpath = os.path.join(idasdkdir, "lib", ea64 and "x86_win_vc_64" or "x86_win_vc_32")
        ida_lib = "ida.lib"
        SWIG_OPTIONS.append("-D__NT__")
        extra_link_parameters = []
        if not args.debug:
            builder.compiler_parameters.append("-Ox")
    # Platform-specific settings for the Mac OS X build
    elif platform == "macosx":
        builder = GCCBuilder()
        builder.linker_parameters.append("-dynamiclib")
        platform_macros = [ "__MAC__" ]
        python_libpath = "."
        python_library = ["-framework", "Python"]
        ida_libpath = os.path.join(idasdkdir, "lib", ea64 and "x86_mac_gcc_64" or "x86_mac_gcc_32")
        ida_lib = ea64 and "-lida64" or "-lida"
        extra_link_parameters = ["-s"]
        builder.compiler_parameters.append("-O3")

    assert builder, "Unknown platform! No idea how to build here..."

    # Enable EA64 for the compiler if necessary
    if ea64:
        platform_macros.append("__EA64__")

    # Build with Hex-Rays decompiler
    if with_hexrays:
        platform_macros.append("WITH_HEXRAYS")
        SWIG_OPTIONS.append('-DWITH_HEXRAYS')

    platform_macros.append("NDEBUG")

    if not '--no-early-load' in sys.argv:
        platform_macros.append("PLUGINFIX")

    # Turn off obsolete functions
    #platform_macros.append("NO_OBSOLETE_FUNCS")

    # Build the wrapper from the interface files
    swig_argv = [SWIG_BIN]
    swig_argv.extend(SWIG_OPTIONS)
    swig_argv.extend(["-Iswig", "-o", "idaapi.cpp"])
    if ea64:
        swig_argv.append("-D__EA64__")
    swig_argv.append("-I%s" % ida_include_directory)
    swig_argv.append("idaapi.i")
#    swigcmd = "%s %s -Iswig -o idaapi.cpp %s -I%s idaapi.i" % (SWIG_BIN, SWIG_OPTIONS, ea64flag, ida_include_directory)
    res = run(swig_argv)
    assert res == 0, "Failed to build the wrapper with SWIG"

    # If we are running on windows, we have to patch some directors'
    # virtual methods, so they have the right calling convention.
    # Without that, compilation just won't succeed.
    if platform == "win32":
        res = run(["python", "patch_directors_cc.py", "-f", "idaapi.h"])
        assert res == 0, "Failed to patch directors' calling conventions"

    # Compile the wrapper
    res = builder.compile("idaapi",
                          includes=[ PYTHON_INCLUDE_DIRECTORY, ida_include_directory ],
                          macros=platform_macros)
    assert res == 0, "Failed to build the wrapper module"

    # Compile the main plugin source
    res =  builder.compile("python",
                           includes=[ PYTHON_INCLUDE_DIRECTORY, ida_include_directory ],
                           macros=platform_macros)
    assert res == 0, "Failed to build the main plugin object"

    # Link the final binary
    libs = []
    libs.extend(python_library)
    libs.append(ida_lib)
    res =  builder.link( ["idaapi", "python"],
                         plugin_name,
                         [ python_libpath, ida_libpath ],
                         libs,
                         extra_link_parameters)
    assert res == 0, "Failed to link the plugin binary"

# -----------------------------------------------------------------------
def detect_platform(ea64):
    # Detect the platform
    system = platform.system()

    if system == "Windows" or system == "Microsoft":
        system = "Windows"
        platform_string = "win32"
        plugin_name = ea64 and "python.p64" or "python.plw"

    elif system == "Linux":
        platform_string = "linux"
        plugin_name = ea64 and "python.plx64" or "python.plx"

    elif system == "Darwin":
        platform_string = "macosx"
        plugin_name = ea64 and "python.pmc64" or "python.pmc"
    else:
        print "Unknown platform!"
        sys.exit(-1)

    return (system, platform_string, plugin_name)

# -----------------------------------------------------------------------
def build_binary_package(ea64, nukeold):
    system, platform_string, plugin_name = detect_platform(ea64)
    BINDISTDIR = "idapython-%d.%d.%d_ida%d.%d_py%d.%d_%s" % (VERSION_MAJOR,
                                                             VERSION_MINOR,
                                                             VERSION_PATCH,
                                                             IDA_MAJOR_VERSION,
                                                             IDA_MINOR_VERSION,
                                                             PYTHON_MAJOR_VERSION,
                                                             PYTHON_MINOR_VERSION,
                                                             platform_string)
    # Build the plugin
    build_plugin(platform_string, IDA_SDK, plugin_name, ea64)

    # Build the binary distribution
    binmanifest = []
    if nukeold:
        binmanifest.extend(BINDIST_MANIFEST)

    if not ea64 or nukeold:
      binmanifest.extend([(x, "python") for x in "python/init.py", "python/idc.py", "python/idautils.py", "idaapi.py"])

    binmanifest.append((plugin_name, "plugins"))

    build_distribution(binmanifest, BINDISTDIR, ea64, nukeold)


# -----------------------------------------------------------------------
def build_source_package():
    """ Build a directory and a ZIP file with all the sources """
    SRCDISTDIR = "idapython-%d.%d.%d" % (VERSION_MAJOR,
                                         VERSION_MINOR,
                                         VERSION_PATCH)
    # Build the source distribution
    srcmanifest = []
    srcmanifest.extend(BINDIST_MANIFEST)
    srcmanifest.extend(SRCDIST_MANIFEST)
    srcmanifest.extend([(x, "python") for x in "python/init.py", "python/idc.py", "python/idautils.py"])
    build_distribution(srcmanifest, SRCDISTDIR, ea64=False, nukeold=True)

# -----------------------------------------------------------------------
def gen_docs(z = False):
        print "Generating documentation....."
        old_dir = os.getcwd()
        try:
            curdir = os.getcwd() + os.sep
            docdir = 'idapython-reference-%d.%d.%d' % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
            sys.path.append(curdir + 'python')
            sys.path.append(curdir + 'tools')
            sys.path.append(curdir + 'docs')
            import epydoc.cli
            import swigdocs
            os.chdir('docs')
            PYWRAPS_FN = 'pywraps'
            swigdocs.gen_docs(outfn = PYWRAPS_FN + '.py')
            epydoc.cli.optparse.sys.argv = [ 'epydoc',
                                             '--no-sourcecode',
                                             '-u', 'http://code.google.com/p/idapython/',
                                             '--navlink', '<a href="http://www.hex-rays.com/idapro/idapython_docs/">IDAPython Reference</a>',
                                             '--no-private',
                                             '--simple-term',
                                             '-o', docdir,
                                             '--html',
                                             'idc', 'idautils', PYWRAPS_FN, 'idaapi']
            # Generate the documentation
            epydoc.cli.cli()

            print "Documentation generated!"

            # Clean temp files
            for f in [PYWRAPS_FN + '.py', PYWRAPS_FN + '.pyc']:
                if os.path.exists(f):
                  os.unlink(f)

            if z:
                z = docdir + '-doc.zip'
                zip = zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED)
                for fn in glob.glob(docdir + os.sep + '*'):
                    zip.write(fn)
                zip.close()
                print "Documentation compressed to", z
        except Exception, e:
            print 'Failed to generate documentation:', e
        finally:
            os.chdir(old_dir)
        return

# -----------------------------------------------------------------------
def usage():
    print """IDAPython build script.

Available switches:
  --doc:
    Generate documentation into the 'docs' directory
  --zip:
    Used with '--doc' switch. It will compress the generated documentation
  --ea64:
    Builds also the 64bit version of the plugin
  --with-hexrays:
    Build with the Hex-Rays Decompiler wrappings
  --no-early-load:
    The plugin will be compiled as normal plugin
    This switch disables processor, plugin and loader scripts
"""

# -----------------------------------------------------------------------
def main():
    if '--help' in sys.argv:
        return usage()
    elif '--doc' in sys.argv:
        return gen_docs(z = '--zip' in sys.argv)

    # # Parse options
    # options = parse_options(sys.argv)
    # ea64 = options[S_EA64]

    # Always build the non __EA64__ version
    build_binary_package(ea64=False, nukeold=True)

    # Rebuild package with __EA64__ if needed
    if args.ea64:
        build_binary_package(ea64=True, nukeold=False)

    # Always build the source package
    build_source_package()

# -----------------------------------------------------------------------
if __name__ == "__main__":
    main()
