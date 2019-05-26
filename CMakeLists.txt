cmake_minimum_required(VERSION 2.8.12)
project(aat)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules/" ${CMAKE_MODULE_PATH} )
find_package(Color)

if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set(WIN32 ON)
endif()

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
option(CMAKE_BUILD_TYPE "Release/Debug build" RELEASE)
option(CPP_BUILD_TESTS "Build the C++ Tests" OFF)
option(CPP_BUILD_STRICT "Build the C++ with strict warnings" OFF)

if(DEFINED ENV{PSP_DEBUG})
    set(CMAKE_BUILD_TYPE DEBUG)
else()
    if (NOT DEFINED CMAKE_BUILD_TYPE)
        set(CMAKE_BUILD_TYPE RELEASE)
    endif()
endif()

if (NOT DEFINED CPP_BUILD_TESTS)
    set(CPP_BUILD_TESTS ON)
endif()

if (NOT DEFINED CPP_BUILD_STRICT)
    set(CPP_BUILD_STRICT OFF)
endif()

message(WARNING "${Cyan}Building C++ binding${ColorReset}")
message(WARNING "${Cyan}Building Python binding${ColorReset}")

if (CPP_BUILD_TESTS)
    message(WARNING "${Cyan}Building C++ tests${ColorReset}")
else()
    message(WARNING "${Cyan}Skipping C++ tests${ColorReset}")
endif()

if (NOT CPP_BUILD_STRICT)
    message(WARNING "${Cyan}Building C++ without strict warnings${ColorReset}")
else()
    message(WARNING "${Cyan}Building C++ with strict warnings${ColorReset}")
endif()

string(TOLOWER "${CMAKE_BUILD_TYPE}" CMAKE_BUILD_TYPE_LOWER )
if(CMAKE_BUILD_TYPE_LOWER STREQUAL debug)
    message(WARNING "${Red}Building DEBUG${ColorReset}")
    add_definitions(-DDEBUG)
else()
    message(WARNING "${Cyan}Building RELEASE${ColorReset}")
endif()

if(BUILD_DOCS)
    message(WARNING "${Cyan}Building Documentation${ColorReset}")
else()
    message(WARNING "${Cyan}Skipping Documentation${ColorReset}")
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


find_package(pybind11)
if(NOT pybind11_FOUND)
    message("${Red}PyBind11 could not be located${ColorReset}")
    build_dep("pybind11", "cmake/Pybind.txt.in")
else()
    message("${Cyan}Found PyBind11 in ${pybind11_INCLUDE_DIRS}${ColorReset}")
endif()
include_directories( ${pybind11_INCLUDE_DIRS} )

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
include_directories("/usr/local/include/python3.7m")  # FIXME
link_directories("/usr/local/lib")  # FIXME
find_package( PythonInterp 3.7 REQUIRED )
include_directories( ${PYTHON_INCLUDE_DIRS} )
find_package(NumPy)
include_directories( ${PYTHON_NUMPY_INCLUDE_DIR})
#####################

if (WIN32)
    set(CMAKE_CXX_FLAGS " /EHsc")
else()
    set(CMAKE_CXX_FLAGS " -std=c++0x ${CMAKE_CXX_FLAGS}")
endif()


if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(CMAKE_SHARED_LIBRARY_SUFFIX .so)
endif()
set(CMAKE_SHARED_LIBRARY_PREFIX "")


include_directories("${CMAKE_SOURCE_DIR}/cpp/include")

########################
# Python extra targets #
########################
add_library(test SHARED
    ${CMAKE_SOURCE_DIR}/cpp/src/test.cpp
    ${HEADER_FILES})
set_target_properties(test PROPERTIES
         LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/aat)
target_link_libraries(test ${BOOST_PYTHON})
target_link_libraries(test ${BOOST_NUMPY})
target_link_libraries(test ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})

add_library(_cpp_helpers SHARED
    ${CMAKE_SOURCE_DIR}/cpp/src/exchanges/_cpp_helpers.cpp)
set_target_properties(_cpp_helpers PROPERTIES
         LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/aat/exchanges)
target_link_libraries(_cpp_helpers test)
target_link_libraries(_cpp_helpers ${BOOST_PYTHON})
target_link_libraries(_cpp_helpers ${BOOST_NUMPY})
target_link_libraries(_cpp_helpers ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
########################

if(CPP_BUILD_STRICT AND NOT WIN32)
    target_compile_options(test PRIVATE -Wall -Werror)
    target_compile_options(test PRIVATE $<$<CONFIG:DEBUG>:-fPIC -O0>)
    target_compile_options(_cpp_helpers PRIVATE -Wall -Werror)
    target_compile_options(_cpp_helpers PRIVATE $<$<CONFIG:DEBUG>:-fPIC -O0>)
endif()


#############
# CPP TESTS #
#############
if (CPP_BUILD_TESTS)
    if (WIN32)
      set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    endif()
    build_dep("googletest" "cmake/GTest.txt.in")

    add_subdirectory(cpp/tests)
    add_custom_target(gcov
        COMMAND mkdir -p ${CMAKE_BINARY_DIR}/coverage
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
    add_custom_command(TARGET gcov
        COMMAND echo "=================== GCOV ===================="
        COMMAND gcovr -r ../ --html --html-details -o coverage/index.html
        COMMAND xdg-open coverage/index.html
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
endif()
#############

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
