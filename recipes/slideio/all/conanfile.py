from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches
from conan.tools.scm import Git
import os


class Slideio(ConanFile):
    name = "slideio"
    url = ""
    version = "2.7.0"
    description = "SlideIO library."
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD 3-Clause"
    package_type = "shared-library"

    def source(self):
         data = self.conan_data["sources"][self.version][0]
         print(data)
         url = data["url"]
         tag = data["tag"]
         args = ["--recurse-submodules", "--depth 1", f"-b {tag}"]
         Git(self).clone(url=url,args=args, target=".")

    def layout(self):
        self.folders.source = "src"
        self.folders.build = os.path.join("src","build")
        
    def export_sources(self):
        export_conandata_patches(self)
        
    def generate(self):
        pass

    def build(self):
        apply_conandata_patches(self)
        configuration = 'release'
        if self.settings.build_type == 'Debug':
            configuration = 'debug'
        python = "python3"
        if self.settings.os == "Windows":
            python = "python"
        self.run(f"{python} install.py -a install -c {configuration}", cwd=self.source_folder)

    def package(self):
        os_name = str(self.settings.os)
        os_dir = os_name
        if os_name == "Macos":
            os_dir = "OSX"
        build_type = str(self.settings.build_type)
        install_folder = os.path.join(self.build_folder, "install")
        print(f"install_folder: {install_folder}")
        copy(self, "*.hpp", src=os.path.join(install_folder,"include"), dst=os.path.join(self.package_folder,"include"))
        lib_pattern = "*.lib"
        bin_pattern = "*.dll"
        if self.settings.os == "Linux":
            lib_pattern = "*.so*"
            bin_pattern = "*.so*"
        elif self.settings.os == "Macos":
            lib_pattern = "*.dylib"
            bin_pattern = "*.dylib"
            
        copy(self, pattern=lib_pattern, dst=os.path.join(self.package_folder,"lib"), src=os.path.join(install_folder, "lib"))
        copy(self, pattern=bin_pattern, dst=os.path.join(self.package_folder, "bin"), src=os.path.join(install_folder, "bin"))
        libs = self.get_shared_libs()

        for lib in libs:
            # copy distributed shared libraries to lib folder
            copy(self, pattern=lib, dst=os.path.join(self.package_folder,"lib"), src=os.path.join(install_folder, "bin"))

        # if self.settings.os == "Linux" or self.settings.os == "Macos":
        #     # copy shared libraries to bin folder
        #     for lib in libs:
        #         self.copy(pattern=lib, dst="bin", src=os.path.join(install_folder, "lib"))

    def get_shared_libs(self):
        lib_names = ["slideio", "slideio-converter", "slideio-transformer", "slideio-core"]
        lib_prefix = ""
        if self.settings.build_type == 'Debug':
            for i in range (len(lib_names)):
                lib_names[i] += "_d"
        lib_suffix = ".lib"
        if self.settings.os == "Linux":
            lib_suffix = ".so"
            lib_prefix = "lib"
        elif self.settings.os == "Macos":
            lib_suffix = ".dylib"
            lib_prefix = "lib"
        for i in range (len(lib_names)):
            lib_names[i] = lib_prefix + lib_names[i] + lib_suffix
        return lib_names

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = self.get_shared_libs()
