from conans import ConanFile, CMake, tools
import os


class GflagsConan(ConanFile):
    name = "gflags"
    description = "The gflags package contains a C++ library that implements commandline flags processing"
    topics = ("conan", "gflags", "cli", "flags", "commandline")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gflags/gflags"
    license = 'BSD-3-Clause'
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "nothreads": [True, False], "namespace": "ANY"}
    default_options = {'shared': False, 'fPIC': True, 'nothreads': True, 'namespace': 'gflags'}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["BUILD_gflags_LIB"] = not self.options.nothreads
        cmake.definitions["BUILD_gflags_nothreads_LIB"] = self.options.nothreads
        cmake.definitions["BUILD_PACKAGING"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["INSTALL_HEADERS"] = True
        cmake.definitions["INSTALL_SHARED_LIBS"] = self.options.shared
        cmake.definitions["INSTALL_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["REGISTER_BUILD_DIR"] = False
        cmake.definitions["REGISTER_INSTALL_PREFIX"] = False
        cmake.definitions["GFLAGS_NAMESPACE"] = self.options.namespace
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    _shared_ext_mapping = {
        "Linux": ".so",
        "Windows": ".dll",
        "Macos": ".dylib",
    }

    _static_ext_mapping = {
        "Linux": ".a",
        "Windows": ".lib",
        "Macos": ".a",
    }

    def package(self):
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        if self.options.shared:
            buildtype = "_shared"
            suffix = self._shared_ext_mapping[str(self.settings.os)]
        else:
            buildtype = "_static"
            suffix = self._static_ext_mapping[str(self.settings.os)]

        name = "gflags" if self.settings.os == "Windows" else "libgflags"
        nothreads = "_nothreads" if self.options.nothreads else ""
        libname = name + nothreads + buildtype + suffix
        tools.rename(os.path.join(self.package_folder, "lib", libname),
                     os.path.join(self.package_folder, "lib", f"gflags{suffix}"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GFLAGS"
        self.cpp_info.filenames["cmake_find_package"] = "gflags"
        self.cpp_info.names["cmake_find_package_multi"] = "GFLAGS"
        self.cpp_info.filenames["cmake_find_package_multi"] = "gflags"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(['shlwapi'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "m"])
