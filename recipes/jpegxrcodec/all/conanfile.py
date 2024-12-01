from conan import ConanFile
from conan.tools.files import save, load
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import unix_path, VCVars, is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.errors import ConanException


class JxrlibConan(ConanFile):
    name = "jpegxrcodec"
    url = ""
    version = "1.0.3"
    description = "Jpeg XR codec."
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    license = "BSD 3-Clause"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        pass
        # if self.settings.os == "Windows":
        #     self.options.remove("fPIC")

    def source(self):
        git = tools.Git()
        git.clone("https://gitlab.com/bioslide/jpegxrcodec.git", "v{0}".format(self.version), args="--recursive")

    def _configure_cmake(self):
        if self.settings.os == "Macos":
            cmake = CMake(self, generator="Xcode")
        else:
            cmake = CMake(self)
        if self.settings.os != "Windows":
           cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = True
        cmake.configure()
        return cmake

    def build(self):
        # ensure that bundled cmake files are not used
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("jxrcodec.hpp", dst="include/jxrcodec", src="jxrcodec")
        if self.settings.os == "Windows":
            src_folder = "bin/" + str(self.settings.build_type)
            self.copy("jxrcodec.*", dst="lib", src=src_folder)
        elif self.settings.os == "Macos":
            src_folder = "bin/" + str(self.settings.build_type)
            self.copy("libjxrcodec.a", dst="lib", src=src_folder)
        else:
            src_folder = str(self.settings.build_type) + "/bin"
            self.copy("libjxrcodec.a", dst="lib", src=src_folder)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["jxrcodec"]
        self.cpp_info.libdirs = ["lib"]
