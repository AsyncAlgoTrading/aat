cmake_minimum_required(VERSION 3.7.2)
project(aat)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG")

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules/" ${CMAKE_MODULE_PATH} )

if(NOT DEFINED AAT_CMAKE_MODULE_PATH)
    set(AAT_CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/../../cmake/")
endif()
set(CMAKE_MODULE_PATH "${AAT_CMAKE_MODULE_PATH}/modules" ${CMAKE_MODULE_PATH})

if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set(WIN32 ON)
    set(MACOS OFF)
    set(LINUX OFF)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(WIN32 OFF)
    set(MACOS ON)
    set(LINUX OFF)
else()
    set(WIN32 OFF)
    set(MACOS OFF)
    set(LINUX ON)
endif()


## Helper function
function(string_starts_with str search)
  string(FIND "${str}" "${search}" out)
  if("${out}" EQUAL 0)
    return(true)
  endif()
  return(false)
endfunction()

##############################
# helper to grab gtest et al #
##############################
function (build_dep name cmake_file)
    if(EXISTS ${CMAKE_BINARY_DIR}/${name}-build)
        message(WARNING "${Cyan}Dependency found - not rebuilding - ${CMAKE_BINARY_DIR}/${name}-build${ColorReset}")
    else()
        configure_file(${cmake_file} ${name}-download/CMakeLists.txt)
        execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
            RESULT_VARIABLE result
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/${name}-download )
        if(result)
            message(FATAL_ERROR "CMake step for ${name} failed: ${result}")
        endif()
        execute_process(COMMAND ${CMAKE_COMMAND} --build .
            RESULT_VARIABLE result
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/${name}-download )
        if(result)
            message(FATAL_ERROR "Build step for ${name} failed: ${result}")
        endif()
    endif()

    add_subdirectory(${CMAKE_BINARY_DIR}/${name}-src
        ${CMAKE_BINARY_DIR}/${name}-build
        EXCLUDE_FROM_ALL)

    include_directories(${CMAKE_BINARY_DIR}/${name}-src/extras/${name}/include)
    include_directories(${CMAKE_BINARY_DIR}/${name}-src/include)
    include_directories(${CMAKE_BINARY_DIR}/${name}-src)
endfunction()
##############################

#######################
# BUILD CONFIGURATION #
#######################
find_package(Color)
option(CMAKE_BUILD_TYPE "Release/Debug build" RELEASE)
option(CPP_BUILD_TESTS "Build the C++ Tests" ON)
option(CPP_BUILD_STRICT "Build the C++ with strict warnings" OFF)

if(DEFINED ENV{DEBUG})
    set(CMAKE_BUILD_TYPE DEBUG)
else()
    if (NOT DEFINED CMAKE_BUILD_TYPE)
        set(CMAKE_BUILD_TYPE RELEASE)
    endif()
endif()

if (NOT DEFINED CPP_BUILD_STRICT)
    set(CPP_BUILD_STRICT OFF)
endif()

if(DEFINED ENV{MANYLINUX})
    set(MANYLINUX ON)
else()
    set(MANYLINUX OFF)
endif()

if(NOT DEFINED AAT_PYTHON_VERSION)
    set(AAT_PYTHON_VERSION 3.7)
endif()


set(BUILD_MESSAGE "")
set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building C++ binding${ColorReset}")
set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building Python binding${ColorReset}")

if (CPP_BUILD_TESTS)
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building C++ tests${ColorReset}")
else()
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Skipping C++ tests${ColorReset}")
endif()

if (NOT CPP_BUILD_STRICT)
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building C++ without strict warnings${ColorReset}")
else()
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building C++ with strict warnings${ColorReset}")
endif()

string(TOLOWER "${CMAKE_BUILD_TYPE}" CMAKE_BUILD_TYPE_LOWER )
if(CMAKE_BUILD_TYPE_LOWER STREQUAL debug)
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Red}Building DEBUG${ColorReset}")
    add_definitions(-DDEBUG)
else()
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building RELEASE${ColorReset}")
endif()

if(BUILD_DOCS)
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Building Documentation${ColorReset}")
else()
    set(BUILD_MESSAGE "${BUILD_MESSAGE}\n${Cyan}Skipping Documentation${ColorReset}")
endif()
#######################

#####################
# VANILLA CPP BUILD #
#####################
if(CMAKE_BUILD_TYPE_LOWER STREQUAL debug)
    set(OPT_FLAGS " \
        -O1 \
        -g3 \
        ")
else()
    set(OPT_FLAGS " \
        -O3 \
        -g0 \
        ")
endif()

set(CMAKE_CXX_FLAGS " \
    ${CMAKE_CXX_FLAGS} \
    ${EXTENDED_FLAGS} \
    ${OPT_FLAGS} \
    ")

message(WARNING "${BUILD_MESSAGE}")

if(WIN32)
    foreach(warning 4244 4251 4267 4275 4290 4786 4305 4996)
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /wd${warning}")
    endforeach(warning)
else()
    include_directories("/usr/local/include")
endif()


#########################
# PYTHON BINDINGS BUILD #
#########################
include_directories("${AAT_PYTHON_SRC}/perspective/include")
if(MANYLINUX)
    # Manylinux docker images have no shared libraries
    # The instead use a statically built python.
    # Cmake's default FindPython can't find the python headers
    # without also finding (or failing to find) the python libraries
    # so we use a custom FindPythonHeaders that is the same as the
    # default, but ignores when the python libraries can't be found.
    message("${Red}Manylinux build has no python shared libraries${ColorReset}")
    find_package( Python ${AAT_PYTHON_VERSION} REQUIRED COMPONENTS Interpreter )
    find_package( PythonHeaders ${AAT_PYTHON_VERSION} REQUIRED)
else()
    message("${Cyan}Use python shared libraries${ColorReset}")
    find_package( Python ${AAT_PYTHON_VERSION} REQUIRED COMPONENTS Interpreter Development)
endif()
message("${Cyan}Using python ${PYTHON_INCLUDE_DIRS} ${Python_LIBRARIES} ${ColorReset}")
include_directories( ${Python_INCLUDE_DIRS} )

# already found from before
find_package(Boost)

if(MACOS)
    # on mac, use the vanilla pybind11 finder
    find_package(pybind11)
    if(pybind11_FOUND)
        # Homebrew install pybind11
        set(PYTHON_PYBIND_FOUND pybind11_FOUND)
    else()
        # see if python installed pybind11 is available
        find_package(Pybind)
        if(PYTHON_PYBIND_FOUND)
            # Need to add extra flags due to pybind weirness
            # https://github.com/pybind/pybind11/blob/7830e8509f2adc97ce9ee32bf99cd4b82089cc4c/tools/pybind11Tools.cmake#L103
            set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -undefined dynamic_lookup")
        endif()
    endif()

else()
    # on linux or in docker, use our custom pybind finder to look 
    # for just the python installed pybind
    find_package(Pybind)
endif()

if(NOT PYTHON_PYBIND_FOUND)
    message("${Red}PyBind11 could not be located${ColorReset}")
    build_dep("pybind11" "${AAT_CMAKE_MODULE_PATH}/Pybind.txt.in")
else()
    message("${Cyan}Found PyBind11 in ${PYTHON_PYBIND_INCLUDE_DIR}${ColorReset}")
    include_directories( ${PYTHON_PYBIND_INCLUDE_DIR} )
endif()

find_package(NumPy)
if(NOT PYTHON_NUMPY_FOUND)
    message(FATAL_ERROR "${Red}Numpy could not be located${ColorReset}")
else()
    message(WARNING "${Cyan}Numpy found: ${PYTHON_NUMPY_INCLUDE_DIR}${ColorReset}")

endif()
include_directories( ${PYTHON_NUMPY_INCLUDE_DIR})
#####################

if (WIN32)
    set(CMAKE_CXX_FLAGS " /EHsc")
else()
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++1y")
    else()
        set(CMAKE_CXX_FLAGS " -std=c++0x ${CMAKE_CXX_FLAGS}")
    endif()
endif()


if(MACOS)
    set(CMAKE_SHARED_LIBRARY_SUFFIX .so)
    
    # Look for the binary using @loader_path (relative to binary location) instead of @rpath
    set(CMAKE_SKIP_BUILD_RPATH FALSE)
    set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)

    if(MACOS)
        set(CMAKE_MACOSX_RPATH 1)
        set(module_install_rpath "@loader_path/")
    else()
        set(module_install_rpath "\$ORIGIN")
    endif()
endif()
set(CMAKE_SHARED_LIBRARY_PREFIX "")


include_directories("${CMAKE_SOURCE_DIR}/cpp/include")

########################
# Python extra targets #
########################
add_library(binding SHARED
    ${CMAKE_SOURCE_DIR}/cpp/src/binding.cpp
    ${HEADER_FILES})
set_target_properties(binding PROPERTIES
         LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/aat)
target_link_libraries(binding ${PYTHON_LIBRARIES})

add_library(_enums SHARED
    ${CMAKE_SOURCE_DIR}/cpp/src/enums.cpp)
set_target_properties(_enums PROPERTIES
         LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/aat)
# target_link_libraries(_enums binding)
target_link_libraries(_enums ${PYTHON_LIBRARIES})

## Copy in place for testing
add_custom_command(TARGET binding POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:binding> ${CMAKE_SOURCE_DIR}/aat/)
add_custom_command(TARGET _enums POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:_enums> ${CMAKE_SOURCE_DIR}/aat/)
########################

if(CPP_BUILD_STRICT AND NOT WIN32)
    target_compile_options(binding PRIVATE -Wall -Werror)
    target_compile_options(binding PRIVATE $<$<CONFIG:DEBUG>:-fPIC -O0>)
    target_compile_options(_enums PRIVATE -Wall -Werror)
    target_compile_options(_enums PRIVATE $<$<CONFIG:DEBUG>:-fPIC -O0>)
endif()


########
# Docs #
########
if(BUILD_DOCS)
    add_custom_target(doxygen)
    add_custom_command(TARGET doxygen
        COMMAND doxygen doxygen.conf
        WORKING_DIRECTORY docs
        COMMENT "Build doxygen xml files used by sphinx/breathe."
    )

    add_custom_target(docs-html ALL)
    add_custom_command(TARGET docs-html
        COMMAND sphinx-build -b html . build/html
            WORKING_DIRECTORY docs
            COMMENT "Build html documentation"
        )
    add_dependencies(docs-html doxygen)

    # add_custom_target(docs-markdown ALL)
    # add_custom_command(TARGET docs-html
    #   COMMAND sphinx-build -M markdown . build/
    #       WORKING_DIRECTORY ../../docs
    #       COMMENT "Build markdown documentation"
    #   )
    # add_dependencies(docs-html doxygen)

endif()
##########
