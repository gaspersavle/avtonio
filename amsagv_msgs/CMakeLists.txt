cmake_minimum_required(VERSION 2.8.3)
project(amsagv_msgs)

##Almost all of the following variables are automatically set, but you can set the initial values.
set(AMSC_MSG_DEP_SET )
set(AMSC_BLD_DEP_SET )
set(AMSC_RUN_DEP_SET )
#System libraries
set(AMSC_SYSTEM_LIBS )
#Link libraries
set(AMSC_LINK_LIBS )
#Force Qt
set(AMSC_USE_QT 0)

##Enable/disable some Qt features
set(QT_USE_QTGUI TRUE)
set(QT_USE_QTOPENGL TRUE)
set(QT_USE_QTXML TRUE)
#set(QT_USE_QTNETWORK TRUE)
#set(QT_USE_QTSQL TRUE)
set(QT_USE_QTSVG TRUE)
#set(QT_USE_QTTEST TRUE)
#set(QT_USE_QTDBUS TRUE)
#set(QT_USE_QTSCRIPT TRUE)
#set(QT_USE_QTWEBKIT TRUE)
#set(QT_USE_QTXMLPATTERNS TRUE)
#set(QT_USE_PHONON TRUE)



#
# Find files: headers (include/.../*.h), modules (src/*.cpp), main modules (srcx/*.cpp), messages (msg/*.msg), services (srv/*.srv) and actions (action/*.action).
#
file(GLOB_RECURSE AMSC_HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} FOLLOW_SYMLINKS include/${PROJECT_NAME}/*.h)
file(GLOB_RECURSE AMSC_SOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} FOLLOW_SYMLINKS src/*.cpp)
file(GLOB_RECURSE AMSC_SOURCEX RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} FOLLOW_SYMLINKS srcx/*.cpp)
file(GLOB AMSC_MSG RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/msg msg/*.msg)
file(GLOB AMSC_SRV RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/srv srv/*.srv)
file(GLOB AMSC_ACTION RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/action action/*.action)

list(LENGTH AMSC_MSG AMSC_MSG_LENGTH)
list(LENGTH AMSC_SRV AMSC_SRV_LENGTH)
list(LENGTH AMSC_ACTION AMSC_ACTION_LENGTH)



#
# Find message dependencies (set AMSC_MSG_DEP_SET from *.msg, *.srv and *.action files)
#
if(${AMSC_MSG_LENGTH} GREATER 0 OR ${AMSC_SRV_LENGTH} GREATER 0 OR ${AMSC_ACTION_LENGTH} GREATER 0)
    list(APPEND AMSC_MSG_DEP_SET std_msgs)
endif()
if(${AMSC_ACTION_LENGTH} GREATER 0)
    list(APPEND AMSC_MSG_DEP_SET actionlib_msgs)
endif()

macro(amsc_find_deps AMSC_TYPE) # LIST
    if(${ARGC} GREATER 1)
        foreach(AMSC_X ${ARGV1})
            file(STRINGS ${CMAKE_CURRENT_SOURCE_DIR}/${AMSC_TYPE}/${AMSC_X} AMSC_Y REGEX "^[ \t]*([a-zA-Z0-9_]+)/")
            foreach(AMSC_Z ${AMSC_Y})
                string(REGEX REPLACE "^[ \t]*([a-zA-Z0-9_]+)/.*" "\\1" AMSC_U ${AMSC_Z})
                list(APPEND AMSC_MSG_DEP_SET ${AMSC_U})
            endforeach()
        endforeach()
    endif()
endmacro(amsc_find_deps)

amsc_find_deps(msg ${AMSC_MSG})
amsc_find_deps(srv ${AMSC_SRV})
amsc_find_deps(action ${AMSC_ACTION})

list(LENGTH AMSC_MSG_DEP_SET AMSC_MSG_DEP_SET_LENGTH)
if(${AMSC_MSG_DEP_SET_LENGTH} GREATER 0)
    list(REMOVE_DUPLICATES AMSC_MSG_DEP_SET)
endif()
list(LENGTH AMSC_MSG_DEP_SET AMSC_MSG_DEP_SET_LENGTH)

if(${AMSC_MSG_DEP_SET_LENGTH} GREATER 0)
    list(APPEND AMSC_BLD_DEP_SET message_generation ${AMSC_MSG_DEP_SET})
    list(APPEND AMSC_RUN_DEP_SET message_runtime ${AMSC_MSG_DEP_SET})
endif()

## In the file package.xml:
##   * add a build_depend and a run_depend tag for each package in AMSC_MSG_DEP_SET
##   * If AMSC_MSG_DEP_SET isn't empty the following dependencies might have been
##     pulled in transitively but can be declared for certainty nonetheless:
##     * add a build_depend tag for "message_generation"
##     * add a run_depend tag for "message_runtime"



##Auto import settings from package.xml
#catkin_package_xml()
#foreach(ITR ${${PROJECT_NAME}_BUILD_DEPENDS})
#    if(ITR MATCHES "(.+)_msgs$" OR ITR MATCHES "^amsc_common$")
#      list(APPEND AMSC_MSG_DEP_SET ${ITR})
#    endif()
#endforeach()
list(APPEND AMSC_BLD_DEP_SET ${${PROJECT_NAME}_BUILD_DEPENDS})
list(APPEND AMSC_RUN_DEP_SET ${${PROJECT_NAME}_RUN_DEPENDS})
#message(STATUS "MSG_DEP = " ${AMSC_MSG_DEP_SET})

list(REMOVE_DUPLICATES AMSC_BLD_DEP_SET)
list(REMOVE_DUPLICATES AMSC_RUN_DEP_SET)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS ${AMSC_BLD_DEP_SET})

## System dependencies are found with CMake's conventions
#find_package(OpenCV REQUIRED)
# find_package(Boost REQUIRED COMPONENTS thread filesystem system)

## Uncomment this if the package has a setup.py. This macro ensures
## modules and global scripts declared therein get installed
## See http://ros.org/doc/api/catkin/html/user_guide/setup_dot_py.html
# catkin_python_setup()

################################################
## Declare ROS messages, services and actions ##
################################################

## Generate messages in the 'msg' folder
if(${AMSC_MSG_LENGTH} GREATER 0)
    add_message_files(
        FILES
        ${AMSC_MSG}
    )
endif()

## Generate services in the 'srv' folder
if(${AMSC_SRV_LENGTH} GREATER 0)
    add_service_files(
        FILES
        ${AMSC_SRV}
    )
endif()

## Generate actions in the 'action' folder
if(${AMSC_ACTION_LENGTH} GREATER 0)
    add_action_files(
        FILES
        ${AMSC_ACTION}
    )
endif()

## Generate added messages and services with any dependencies listed here
if(${AMSC_MSG_LENGTH} GREATER 0 OR ${AMSC_SRV_LENGTH} GREATER 0 OR ${AMSC_ACTION_LENGTH} GREATER 0)
    if(${AMSC_MSG_DEP_SET_LENGTH} GREATER 0)
        generate_messages(
            DEPENDENCIES
            ${AMSC_MSG_DEP_SET}
        )
    else()
        generate_messages()
    endif()
endif()

########
## Qt ##
########
file(GLOB AMSC_FORMS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ui/*.ui)
file(GLOB AMSC_RESOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} resources/*.qrc)
set(AMSC_MOC )
foreach(AMSC_HEADER ${AMSC_HEADERS})
    file(STRINGS ${AMSC_HEADER} AMSC_TMP REGEX "^[ \t]*Q_OBJECT[ \t\r\n]*")
    list(LENGTH AMSC_TMP AMSC_TMP_LENGTH)
    if(${AMSC_TMP_LENGTH} GREATER 0)
        list(APPEND AMSC_MOC ${AMSC_HEADER})
    endif()
endforeach()

list(LENGTH AMSC_FORMS AMSC_FORMS_LENGTH)
list(LENGTH AMSC_RESOURCES AMSC_RESOURCES_LENGTH)
list(LENGTH AMSC_MOC AMSC_MOC_LENGTH)

if(${AMSC_USE_QT} OR ${AMSC_FORMS_LENGTH} GREATER 0 OR ${AMSC_RESOURCES_LENGTH} GREATER 0 OR ${AMSC_MOC_LENGTH} GREATER 0)
    find_package(Qt4 REQUIRED)

    include(${QT_USE_FILE})
    add_definitions(-DQT_NO_KEYWORDS)
    add_definitions(${QT_DEFINITIONS})

    qt4_add_resources(AMSC_RESOURCES_CPP ${AMSC_RESOURCES})
    qt4_wrap_ui(AMSC_FORMS_HPP ${AMSC_FORMS})
    qt4_wrap_cpp(AMSC_MOC_HPP ${AMSC_MOC})
    #qt4_automoc(${AMSC_SOURCES})
else()
    set(AMSC_RESOURCES_CPP )
    set(AMSC_FORMS_HPP )
    set(AMSC_MOC_CPP )
endif()

set(AMSC_ALL_LIBS ${catkin_LIBRARIES} ${QT_LIBRARIES} ${OpenCV_LIBS} ${Boost_LIBRARIES} ${AMSC_LINK_LIBS})
set(AMSC_ALL_INCLUDE include ${catkin_INCLUDE_DIRS} ${OpenCV_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS})
set(AMSC_ALL_SOURCES ${AMSC_SOURCES} ${AMSC_RESOURCES_CPP} ${AMSC_MOC_HPP} ${AMSC_FORMS_HPP} ${AMSC_HEADERS})
list(LENGTH AMSC_ALL_SOURCES AMSC_ALL_SOURCES_LENGTH)

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
if(${AMSC_ALL_SOURCES_LENGTH} GREATER 0)
    catkin_package(
        INCLUDE_DIRS include
        LIBRARIES ${PROJECT_NAME}
        CATKIN_DEPENDS ${AMSC_RUN_DEP_SET}
        DEPENDS ${AMSC_SYSTEM_LIBS}
    )
else()
    catkin_package(
        CATKIN_DEPENDS ${AMSC_RUN_DEP_SET}
        DEPENDS ${AMSC_SYSTEM_LIBS}
    )
endif()

add_definitions(-fwide-exec-charset=utf-8)
add_definitions(-std=c++17)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(${AMSC_ALL_INCLUDE})
#link_directories(/usr/lib/x86_64-linux-gnu/)

#common commands for building c++ executables and libraries
if(${AMSC_ALL_SOURCES_LENGTH} GREATER 0)
    add_library(${PROJECT_NAME} ${AMSC_ALL_SOURCES})
    if(${AMSC_MSG_LENGTH} GREATER 0 OR ${AMSC_SRV_LENGTH} GREATER 0 OR ${AMSC_ACTION_LENGTH} GREATER 0)
        add_dependencies(${PROJECT_NAME} ${catkin_EXPORTED_TARGETS})
        add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}_generate_messages_cpp)
    endif()
    target_link_libraries(${PROJECT_NAME} ${AMSC_ALL_LIBS})
endif()

foreach(AMSC_SRCX ${AMSC_SOURCEX})
    get_filename_component(AMSC_X ${AMSC_SRCX} NAME_WE)
    add_executable(${PROJECT_NAME}__${AMSC_X} ${AMSC_SRCX})
    set_target_properties(${PROJECT_NAME}__${AMSC_X} PROPERTIES OUTPUT_NAME ${AMSC_X})
    if(${AMSC_ALL_SOURCES_LENGTH} GREATER 0)
        target_link_libraries(${PROJECT_NAME}__${AMSC_X} ${PROJECT_NAME})
    else()
        target_link_libraries(${PROJECT_NAME}__${AMSC_X} ${AMSC_ALL_LIBS})
    endif()
endforeach()

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
# install(PROGRAMS
#   scripts/my_python_script
#   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark executables and/or libraries for installation
# install(TARGETS primer primer_node
#   ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark cpp header files for installation
# install(DIRECTORY include/${PROJECT_NAME}/
#   DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
#   FILES_MATCHING PATTERN "*.h"
#   PATTERN ".svn" EXCLUDE
# )

## Mark other files for installation (e.g. launch and bag files, etc.)
# install(FILES
#   # myfile1
#   # myfile2
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
# )

#############
## Testing ##
#############

## Add gtest based cpp test target and link libraries
# catkin_add_gtest(${PROJECT_NAME}-test test/test_primer.cpp)
# if(TARGET ${PROJECT_NAME}-test)
#   target_link_libraries(${PROJECT_NAME}-test ${PROJECT_NAME})
# endif()

## Add folders to be run by python nosetests
# catkin_add_nosetests(test)
