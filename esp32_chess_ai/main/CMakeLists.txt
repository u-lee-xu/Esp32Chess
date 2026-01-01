idf_component_register(SRCS "chess_ai.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES esp_timer driver)
idf_component_get_property(esptflitemicro_lib espressif__esp-tflite-micro COMPONENT_LIB)
target_link_libraries(${COMPONENT_LIB} PRIVATE ${esptflitemicro_lib})