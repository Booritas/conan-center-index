from conan import ConanFile
from conan.tools.files import save, load
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import unix_path, VCVars, is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.errors import ConanException
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Git
import os

def find_file_recursively(folder, filename):
    for root, dirs, files in os.walk(folder):
        if filename in files:
            return os.path.join(root, filename)
    return None

class JxrlibConan(ConanFile):
    name = "jpegxrcodec"
    url = ""
    version = "1.0.3"
    description = "Jpeg XR codec."
    settings = "os", "compiler", "build_type", "arch"
    #generators = "CMakeDeps", "CMakeToolchain"
    license = "BSD 3-Clause"

    def config_options(self):
        pass

    def source(self):
         data = self.conan_data["sources"][self.version][0]
         print(data)
         url = data["url"]
         tag = data["tag"]
         args = ["--recurse-submodules", "--depth 1", f"-b {tag}"]
         Git(self).clone(url=url,args=args, target=".")

    def layout(self):
        cmake_layout(self, src_folder="source_subfolder")

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os != "Windows":
           tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = True
        tc.generate()


    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        target_include_dir = os.path.join(self.package_folder, "include", "jxrcodec")
        source_include_dir = os.path.join(self.source_folder, "jxrcodec")
        copy(self, "jxrcodec.hpp", source_include_dir, target_include_dir)
        
        target_lib_dir = os.path.join(self.package_folder, "lib")
        libfile = "libjxrcodec.a"
        if self.settings.os == "Windows":
            libfile = "jxrcodec.lib"
            
        lib = find_file_recursively(self.build_folder, libfile)
        if lib:
            lib_dir, lib_name = os.path.split(lib)
            copy(self, lib_name, lib_dir, target_lib_dir)
        
        

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["jxrcodec"]
        self.cpp_info.libdirs = ["lib"]
