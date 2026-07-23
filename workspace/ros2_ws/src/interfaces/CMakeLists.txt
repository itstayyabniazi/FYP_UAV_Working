cmake_minimum_required(VERSION 3.8)
project(interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ----------------------------------------------------------
# Dependencies
# ----------------------------------------------------------

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

# ----------------------------------------------------------
# Generate ROS Messages
# ----------------------------------------------------------

rosidl_generate_interfaces(${PROJECT_NAME}

  "msg/UAVState.msg"
  "msg/PlatformState.msg"
  "msg/LandingTarget.msg"
  "msg/RLObservation.msg"
  "msg/LandingCommand.msg"

  DEPENDENCIES
  builtin_interfaces
)

# ----------------------------------------------------------

ament_export_dependencies(rosidl_default_runtime)

ament_package()
