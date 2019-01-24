import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibRealsenseConan(ConanFile):
    version = "2.17.1"

    name = "librealsense"
    license = "https://raw.githubusercontent.com/IntelRealSense/librealsense/master/LICENSE"
    description = "Intel RealSense SDK https://realsense.intel.com"
    url = "https://github.com/ulricheck/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "with_examples": [True, False],
        }

    default_options = (
        "shared=False",
        "with_examples=False",
        )

    requires = (
        "glfw/[>=3.2.1]@camposs/stable",
        )

    # The folder name when the *.tar.gz release is extracted
    folder_name = "librealsense-%s" % version
    # The name of the archive that is downloaded from Github
    archive_name = "%s.tar.gz" % folder_name
    # The temporary build diirectory
    build_dir = "./%s/build" % folder_name

    def source(self):
        tools.download(
            "https://github.com/IntelRealSense/librealsense/archive/v%s.tar.gz" % self.version,
            self.archive_name
        )
        tools.untargz(self.archive_name)
        os.unlink(self.archive_name)

    def build(self):
        files.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)
            cmake.definitions["BUILD_EXAMPLES"] = self.options.with_examples

            # if self.settings.os == "Linux":
                # for now disable graphical examples .. problem with glfw linking / x11
                # cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = "OFF"
            # else:
            cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = self.options.with_examples

            # don't build additional examples
            cmake.definitions["BUILD_PCL_EXAMPLES"] = "OFF"
            cmake.definitions["BUILD_NODEJS_BINDINGS"] = "OFF"
            cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"
            cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"

            # hints to find GLFW
            cmake.definitions["CMAKE_INCLUDE_PATH"] = ":".join(self.deps_cpp_info["glfw"].include_paths)
            cmake.definitions["CMAKE_LIBRARY_PATH"] = ":".join(self.deps_cpp_info["glfw"].lib_paths)


            # what is this ??
            cmake.definitions["ENABLE_ZERO_COPY"] = "OFF"
            cmake.definitions["BUILD_RS400_EXTRAS"] = True

            if self.options.shared:
                cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
                cmake.definitions["BUILD_WITH_STATIC_CRT"] = "OFF"
                if tools.os_info.is_macos:
                    cmake.definitions["CMAKE_MACOSX_RPATH"] = "ON"
            else:
                cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"

            cmake.configure(source_dir="..", build_dir=".")
            cmake.build(build_dir=".")
            cmake.install()
            os.rename("../LICENSE", "../LICENSE.LibRealSense")

    def package(self):
        self.copy("LICENSE.LibRealSense", src=self.folder_name)

    def package_info(self):
        libs = tools.collect_libs(self)
        self.cpp_info.libs = [l for l in libs if "realsense-file" not in l]
        self.user_info.realsense_file_library_name = [l for l in libs if "realsense-file" in l][0]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
