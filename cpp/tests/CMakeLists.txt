set (TEST_FILES
    src/aat.cpp
    src/simple.cpp
)

include_directories("include")
add_executable(aat_test ${TEST_FILES})
set_target_properties(aat_test PROPERTIES
         RUNTIME_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/aat/tests)

if(WIN32)
	target_compile_definitions(aat_test PRIVATE WIN32=1)
endif()

target_link_libraries(aat_test binding gtest_main)
add_test(NAME aattest COMMAND aat_test)
