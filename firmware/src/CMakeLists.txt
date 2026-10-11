idf_component_register(SRCS "main.cpp" "display.cpp" "buttons.cpp" "resources.cpp"
    INCLUDE_DIRS "." "../life_counter_5641as"
    REQUIRES esp_driver_gpio esp_timer esp_rom freertos log)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror)
