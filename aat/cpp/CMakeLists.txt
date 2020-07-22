cmake_minimum_required(VERSION 3.7.2)
project(aat)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

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

#######################
# BUILD CONFIGURATION #
#######################
if(NOT WIN32)
  string(ASCII 27 Esc)
  set(ColorReset "${Esc}[m")
  set(Red     "${Esc}[1;31m")
  set(Green   "${Esc}[1;32m")
  set(Yellow  "${Esc}[1;33m")
  set(Blue    "${Esc}[1;34m")
  set(Magenta "${Esc}[1;35m")
  set(Cyan    "${Esc}[1;36m")
  set(White   "${Esc}[1;37m")
endif()

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

set(BUILD_MESSAGE "")
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

#############
# CPP BUILD #
#############
if(CMAKE_BUILD_TYPE_LOWER STREQUAL debug)
    set(FLAGS " \
        -O1 \
        -DEBUG
        -g3 \
        ")
else()
    set(FLAGS " \
        -O3 \
        -DNDEBUG
        -g0 \
        ")
endif()

set(CMAKE_CXX_FLAGS " \
    ${CMAKE_CXX_FLAGS} \
    ${OPT_FLAGS} \
    ")
set(CMAKE_C_FLAGS " \
    ${CMAKE_C_FLAGS} \
    ${OPT_FLAGS} \
    ")


message(WARNING "${BUILD_MESSAGE}")

if(WIN32)
    foreach(warning 4244 4251 4267 4275 4290 4786 4305 4996)
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /wd${warning}")
    endforeach(warning)
    add_definitions(-DHAVE_SNPRINTF)
else()
    include_directories("/usr/local/include")
endif()

include_directories(${CMAKE_SOURCE_DIR}/third/date)
include_directories(${CMAKE_SOURCE_DIR}/third/nlohmann_json)
include_directories(${CMAKE_SOURCE_DIR}/third/pybind11)
include_directories(${CMAKE_SOURCE_DIR}/third/pybind11_json)
#####################

if (WIN32)
    set(CMAKE_CXX_FLAGS " /EHsc -DHAVE_SNPRINTF")
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


include_directories("${CMAKE_SOURCE_DIR}/include")

set(SOURCE_FILES
    ${CMAKE_SOURCE_DIR}/src/config/enums.cpp
    ${CMAKE_SOURCE_DIR}/src/config/parser.cpp
    ${CMAKE_SOURCE_DIR}/src/core/instrument/instrument.cpp
    ${CMAKE_SOURCE_DIR}/src/core/exchange/exchange.cpp
    ${CMAKE_SOURCE_DIR}/src/core/models/data.cpp
    ${CMAKE_SOURCE_DIR}/src/core/models/event.cpp
    ${CMAKE_SOURCE_DIR}/src/core/models/order.cpp
    ${CMAKE_SOURCE_DIR}/src/core/models/position.cpp
    ${CMAKE_SOURCE_DIR}/src/core/models/trade.cpp
    ${CMAKE_SOURCE_DIR}/src/core/order_book/price_level.cpp
    ${CMAKE_SOURCE_DIR}/src/core/order_book/collector.cpp
    ${CMAKE_SOURCE_DIR}/src/core/order_book/order_book.cpp
)

###########
# targets #
###########
add_library(aat SHARED ${SOURCE_FILES})
########################

if(CPP_BUILD_STRICT AND NOT WIN32)
    target_compile_options(aat PRIVATE -Wall -Werror)
    target_compile_options(aat PRIVATE $<$<CONFIG:DEBUG>:-fPIC -O0>)
endif()
