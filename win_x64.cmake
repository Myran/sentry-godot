# CMake toolchain file for x64 Windows builds
# Forces AMD64 processor to prevent ARM auto-detection on ARM64 machines
# Used by sentry-native build on Windows VM

set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR AMD64)
set(CMAKE_GENERATOR_PLATFORM x64)
