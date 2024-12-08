from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches
from conan.tools.scm import Git
import os


class PoleConan(ConanFile):
    name = "pole"
    url = ""
    description = "portable library for structured storagec."
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD 3-Clause"

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
        tc.variables['PACKAGE_TESTS'] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*",  src=os.path.join(self.build_folder,"install","includes"), dst=os.path.join(self.package_folder, "include", "pole"))
        copy(self, "*", src=os.path.join(self.build_folder,"install","lib"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["pole"]
        self.cpp_info.libdirs = ["lib"]
