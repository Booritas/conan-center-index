from conan import ConanFile
from conan.tools.files import save, load, rmdir, rm
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import unix_path, VCVars, is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.errors import ConanException
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Git
import os


class LibjpegTurboConan(ConanFile):
    name = "ndpi-libjpeg-turbo"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    license = "BSD-3-Clause, Zlib"
    homepage = "https://libjpeg-turbo.org"
    topics = ("jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    provides = "libjpeg"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "SIMD": [True, False],
        "arithmetic_encoder": [True, False],
        "arithmetic_decoder": [True, False],
        "libjpeg7_compatibility": [True, False],
        "libjpeg8_compatibility": [True, False],
        "mem_src_dst": [True, False],
        "turbojpeg": [True, False],
        "java": [True, False],
        "enable12bit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "SIMD": True,
        "arithmetic_encoder": True,
        "arithmetic_decoder": True,
        "libjpeg7_compatibility": True,
        "libjpeg8_compatibility": True,
        "mem_src_dst": True,
        "turbojpeg": True,
        "java": False,
        "enable12bit": False,
    }

    def source(self):
         data = self.conan_data["sources"][self.version][0]
         print(data)
         url = data["url"]
         tag = data["tag"]
         args = ["--recurse-submodules", "--depth 1", f"-b {tag}"]
         Git(self).clone(url=url,args=args, target=".")
         
    def layout(self):
            cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.options.enable12bit and (self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility):
            raise ConanInvalidConfiguration("12-bit samples is not allowed with libjpeg v7/v8 API/ABI")
        if self.options.get_safe("java", False) and not self.options.shared:
            raise ConanInvalidConfiguration("java wrapper requires shared libjpeg-turbo")
        if is_msvc(self) and self.options.shared and str(self.settings.compiler.runtime).startswith("MT"):
            raise ConanInvalidConfiguration("shared libjpeg-turbo can't be built with MT or MTd")

    @property
    def _is_arithmetic_encoding_enabled(self):
        return self.options.get_safe("arithmetic_encoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    @property
    def _is_arithmetic_decoding_enabled(self):
        return self.options.get_safe("arithmetic_decoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility


    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os != "Windows":
           tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = True
        tc.variables["CONAN_DISABLE_CHECK_COMPILER"] = True
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["WITH_SIMD"] = self.options.get_safe("SIMD", False)
        tc.variables["WITH_ARITH_ENC"] = self._is_arithmetic_encoding_enabled
        tc.variables["WITH_ARITH_DEC"] = self._is_arithmetic_decoding_enabled
        tc.variables["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        tc.variables["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        tc.variables["WITH_MEM_SRCDST"] = self.options.get_safe("mem_src_dst", False)
        tc.variables["WITH_TURBOJPEG"] = self.options.get_safe("turbojpeg", False)
        tc.variables["WITH_JAVA"] = self.options.get_safe("java", False)
        tc.variables["WITH_12BIT"] = self.options.enable12bit
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "README.ijg", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "doc"))
        # remove binaries and pdb files
        for pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            rm(self, pattern_to_remove, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        #self.cpp_info.set_property("cmake_module_file_name", "NDPIJPEG")
        self.cpp_info.set_property("cmake_file_name", "NDPIJPEG")
        self.cpp_info.set_property("cmake_target_name", "NDPIJPEG::NDPIJPEG")

        cmake_target_suffix = "-static" if not self.options.shared else ""
        lib_suffix = "-static" if is_msvc(self) and not self.options.shared else ""

        #self.cpp_info.components["jpeg"].set_property("cmake_module_target_name", "NDPIJPEG::NDPIJPEG")
        #self.cpp_info.components["jpeg"].set_property("cmake_target_name", f"libjpeg-turbo::jpeg{cmake_target_suffix}")
        #self.cpp_info.components["jpeg"].set_property("pkg_config_name", "libjpeg")
        self.cpp_info.components["jpeg"].libs = [f"jpeg{lib_suffix}"]

        if self.options.get_safe("turbojpeg"):
            self.cpp_info.components["turbojpeg"].set_property("cmake_target_name", f"libjpeg-turbo::turbojpeg{cmake_target_suffix}")
            self.cpp_info.components["turbojpeg"].set_property("pkg_config_name", "libturbojpeg")
            self.cpp_info.components["turbojpeg"].libs = [f"turbojpeg{lib_suffix}"]
